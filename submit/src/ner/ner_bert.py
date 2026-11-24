#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BERT-CRF 命名实体识别（中文）。

准备 BIO 训练数据 data/train.bio（每行「字<TAB>标签」，空行分隔句子）后：

    python src/ner/ner_bert.py --train data/train.bio
    python src/ner/ner_bert.py --eval  data/test.bio
    python src/ner/ner_bert.py --predict "孙少平到原西县高中读书"

首次运行会自动下载 bert-base-chinese（需网络）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(HERE))

from config import (BATCH_SIZE, BERT_MODEL, EPOCHS_BERT, ID2TAG, LR_BERT,
                    MAX_LEN, OUTPUT, SEED, TAG2ID)
from crf import CRF
from utils import evaluate_spans, extract_entities, load_bio

torch.manual_seed(SEED)


class NerDataset(Dataset):
    """把字级 BIO 标签对齐到 WordPiece / 中文字 token。"""

    def __init__(self, samples, tokenizer, max_len=MAX_LEN):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        chars, tags = self.samples[idx]
        enc = self.tokenizer(chars, is_split_into_words=True, truncation=True,
                             max_length=self.max_len, return_tensors="pt")
        labels, prev = [], None
        for wid in enc.word_ids():
            if wid is None:
                labels.append(-100)
            elif wid != prev:
                labels.append(TAG2ID.get(tags[wid], 0))
                prev = wid
            else:
                labels.append(-100)
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(labels, dtype=torch.long),
        }


def collate_fn(batch, pad_id=0):
    n = max(len(b["input_ids"]) for b in batch)
    ids, masks, labels = [], [], []
    for b in batch:
        p = n - len(b["input_ids"])
        ids.append(F.pad(b["input_ids"], (0, p), value=pad_id))
        masks.append(F.pad(b["attention_mask"], (0, p), value=0))
        labels.append(F.pad(b["labels"], (0, p), value=-100))
    return torch.stack(ids), torch.stack(masks), torch.stack(labels)


class BertCrf(torch.nn.Module):
    def __init__(self, model_name=BERT_MODEL, num_tags=len(TAG2ID)):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.classifier = torch.nn.Linear(self.bert.config.hidden_size, num_tags)
        self.crf = CRF(num_tags)

    def forward(self, input_ids, attention_mask, labels=None):
        h = self.bert(input_ids, attention_mask=attention_mask).last_hidden_state
        emissions = self.classifier(h)
        if labels is not None:
            return self.crf(emissions, labels, mask=attention_mask.bool()), emissions
        return emissions


def build_loader(samples, tokenizer, batch_size=BATCH_SIZE, shuffle=False):
    return DataLoader(NerDataset(samples, tokenizer), batch_size=batch_size,
                      shuffle=shuffle, collate_fn=collate_fn)


def train(model, loader, optimizer, device, epochs=EPOCHS_BERT):
    model.train()
    for epoch in range(1, epochs + 1):
        total = 0.0
        for ids, masks, labels in loader:
            ids, masks, labels = ids.to(device), masks.to(device), labels.to(device)
            loss, _ = model(ids, masks, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()
            total += loss.item()
        print(f"epoch {epoch}/{epochs}  loss={total / len(loader):.4f}")
    path = OUTPUT / "models" / "bert_ner.pt"
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)
    print(f"[OK] 模型已保存: {path}")


def evaluate(model, loader, device):
    model.eval()
    preds, golds = [], []
    with torch.no_grad():
        for ids, masks, labels in loader:
            emissions = model(ids.to(device), masks.to(device))
            for p, g in zip(model.crf.decode(emissions, masks.bool().to(device)), labels):
                preds.append(p)
                golds.append(g.tolist())
    return evaluate_spans(preds, golds, ID2TAG)


def predict(model, tokenizer, text, device, max_len=MAX_LEN):
    chars = list(text)
    enc = tokenizer(chars, is_split_into_words=True, truncation=True,
                    max_length=max_len, return_tensors="pt")
    ids, masks = enc["input_ids"].to(device), enc["attention_mask"].to(device)
    with torch.no_grad():
        tags = model.crf.decode(model(ids, masks), masks.bool())[0]
    token_tags = [ID2TAG.get(t, "O") for t in tags]
    result, prev = [], None
    for word_id, tag in zip(enc.word_ids(), token_tags):
        if word_id is None or word_id == prev:
            continue
        prev = word_id
        result.append((chars[word_id], tag))
    return result


def main():
    parser = argparse.ArgumentParser(description="BERT-CRF 命名实体识别")
    parser.add_argument("--train", type=Path)
    parser.add_argument("--eval", type=Path)
    parser.add_argument("--predict", type=str)
    parser.add_argument("--model", default=BERT_MODEL)
    parser.add_argument("--epochs", type=int, default=EPOCHS_BERT)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = BertCrf(args.model).to(device)

    if args.train:
        samples = load_bio(args.train)
        loader = build_loader(samples, tokenizer, shuffle=True)
        optimizer = torch.optim.AdamW(model.parameters(), lr=LR_BERT)
        train(model, loader, optimizer, device, args.epochs)
    if args.eval:
        ckpt = OUTPUT / "models" / "bert_ner.pt"
        if ckpt.exists():
            model.load_state_dict(torch.load(ckpt, map_location=device))
        samples = load_bio(args.eval)
        print("评估结果:", evaluate(model, build_loader(samples, tokenizer), device))
    if args.predict:
        ckpt = OUTPUT / "models" / "bert_ner.pt"
        if ckpt.exists():
            model.load_state_dict(torch.load(ckpt, map_location=device))
        for ch, tag in predict(model, tokenizer, args.predict, device):
            print(f"{ch}\t{tag}")


if __name__ == "__main__":
    main()
