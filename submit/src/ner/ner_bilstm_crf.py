#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BiLSTM-CRF 命名实体识别（字向量 + 双向 LSTM + CRF）。

    python src/ner/ner_bilstm_crf.py --train data/train.bio
    python src/ner/ner_bilstm_crf.py --eval  data/test.bio
    python src/ner/ner_bilstm_crf.py --predict "孙少平到原西县高中读书"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from torch.nn.utils.rnn import pad_sequence

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

from config import (BATCH_SIZE, DROPOUT, EMBED_DIM, EPOCHS_BILSTM, HIDDEN_DIM,
                    ID2TAG, LR_BILSTM, OUTPUT, SEED, TAG2ID)
from crf import CRF
from utils import evaluate_spans, extract_entities, load_bio

torch.manual_seed(SEED)
PAD = "<PAD>"
UNK = "<UNK>"


def build_vocab(samples):
    chars = {ch for chars_, _ in samples for ch in chars_}
    vocab = {PAD: 0, UNK: 1}
    for ch in sorted(chars):
        vocab[ch] = len(vocab)
    return vocab


class CharDataset(Dataset):
    def __init__(self, samples, vocab):
        self.data = [(
            torch.tensor([vocab.get(c, 1) for c in chars], dtype=torch.long),
            torch.tensor([TAG2ID.get(t, 0) for t in tags], dtype=torch.long),
        ) for chars, tags in samples]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


def collate_fn(batch):
    xs, ys = zip(*batch)
    length = torch.tensor([len(x) for x in xs])
    return (pad_sequence(xs, batch_first=True, padding_value=0),
            pad_sequence(ys, batch_first=True, padding_value=-100),
            length)


class BiLstmCrf(torch.nn.Module):
    def __init__(self, vocab_size, num_tags=len(TAG2ID), embed_dim=EMBED_DIM,
                 hidden_dim=HIDDEN_DIM, dropout=DROPOUT):
        super().__init__()
        self.embed = torch.nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = torch.nn.LSTM(embed_dim, hidden_dim // 2, batch_first=True,
                                  bidirectional=True, dropout=dropout, num_layers=2)
        self.classifier = torch.nn.Linear(hidden_dim, num_tags)
        self.crf = CRF(num_tags)

    def forward(self, x, length, labels=None):
        mask = torch.arange(x.size(1), device=x.device).unsqueeze(0) < length.unsqueeze(1)
        h, _ = self.lstm(self.embed(x))
        emissions = self.classifier(h)
        if labels is not None:
            return self.crf(emissions, labels, mask=mask), emissions, mask
        return emissions, mask


def train(model, loader, optimizer, device, epochs=EPOCHS_BILSTM):
    model.train()
    for epoch in range(1, epochs + 1):
        total = 0.0
        for x, y, length in loader:
            x, y, length = x.to(device), y.to(device), length.to(device)
            loss, _, _ = model(x, length, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            optimizer.zero_grad()
            total += loss.item()
        print(f"epoch {epoch}/{epochs}  loss={total / len(loader):.4f}")
    path = OUTPUT / "models" / "bilstm_crf_ner.pt"
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state": model.state_dict(), "vocab": model.vocab}, path)
    print(f"[OK] 模型已保存: {path}")


def evaluate(model, loader, device):
    model.eval()
    preds, golds = [], []
    with torch.no_grad():
        for x, y, length in loader:
            emissions, mask = model(x.to(device), length.to(device))
            for p, g in zip(model.crf.decode(emissions, mask), y):
                preds.append(p)
                golds.append(g.tolist())
    return evaluate_spans(preds, golds, ID2TAG)


def main():
    parser = argparse.ArgumentParser(description="BiLSTM-CRF 命名实体识别")
    parser.add_argument("--train", type=Path)
    parser.add_argument("--eval", type=Path)
    parser.add_argument("--predict", type=str)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = OUTPUT / "models" / "bilstm_crf_ner.pt"

    if args.train:
        samples = load_bio(args.train)
        vocab = build_vocab(samples)
        model = BiLstmCrf(len(vocab)).to(device)
        model.vocab = vocab
        loader = DataLoader(CharDataset(samples, vocab), batch_size=BATCH_SIZE,
                            shuffle=True, collate_fn=collate_fn)
        train(model, loader, torch.optim.Adam(model.parameters(), lr=LR_BILSTM), device, args.epochs)
        return

    if not ckpt.exists():
        raise SystemExit(f"未找到模型 {ckpt}，请先 --train")
    state = torch.load(ckpt, map_location=device)
    model = BiLstmCrf(len(state["vocab"])).to(device)
    model.load_state_dict(state["state"])
    model.vocab = state["vocab"]

    if args.eval:
        samples = load_bio(args.eval)
        loader = DataLoader(CharDataset(samples, model.vocab), batch_size=BATCH_SIZE,
                            collate_fn=collate_fn)
        print("评估结果:", evaluate(model, loader, device))
    if args.predict:
        x = torch.tensor([[model.vocab.get(c, 1) for c in args.predict]], dtype=torch.long)
        length = torch.tensor([len(args.predict)])
        emissions, mask = model(x.to(device), length.to(device))
        tags = model.crf.decode(emissions, mask)[0]
        for ch, tid in zip(args.predict, tags):
            print(f"{ch}\t{ID2TAG.get(tid, 'O')}")


if __name__ == "__main__":
    main()
