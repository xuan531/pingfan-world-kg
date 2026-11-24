#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BERT 关系分类器：把 (句子, 头实体, 尾实体) 编码为关系类别。

训练数据格式 JSON 数组：
[{"text": "...", "head": "孙少安", "tail": "贺秀莲", "relation": "SPOUSE"}, ...]

    python src/relation/relation_bert.py --train data/rel_train.json
    python src/relation/relation_bert.py --predict "孙少安与秀莲结了婚|孙少安|秀莲"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import BATCH_SIZE, BERT_MODEL, LR_BERT, MAX_LEN, OUTPUT, SEED

torch.manual_seed(SEED)


class RelDataset(Dataset):
    def __init__(self, samples, tokenizer, rel2id, max_len=MAX_LEN):
        self.samples = samples
        self.tokenizer = tokenizer
        self.rel2id = rel2id
        self.max_len = max_len

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        enc = self.tokenizer(
            s["text"], f'{s["head"]}[SEP]{s["tail"]}',
            truncation=True, max_length=self.max_len, return_tensors="pt",
        )
        return {k: v.squeeze(0) for k, v in enc.items()} | {
            "label": self.rel2id[s["relation"]]
        }


def collate_fn(batch, pad_id=0):
    n = max(len(b["input_ids"]) for b in batch)
    ids, masks, labels = [], [], []
    for b in batch:
        p = n - len(b["input_ids"])
        ids.append(torch.nn.functional.pad(b["input_ids"], (0, p), value=pad_id))
        masks.append(torch.nn.functional.pad(b["attention_mask"], (0, p), value=0))
        labels.append(b["label"])
    return torch.stack(ids), torch.stack(masks), torch.tensor(labels)


class BertRelation(torch.nn.Module):
    def __init__(self, model_name=BERT_MODEL, num_relations=32):
        super().__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.classifier = torch.nn.Linear(self.bert.config.hidden_size, num_relations)

    def forward(self, ids, masks):
        h = self.bert(ids, attention_mask=masks).last_hidden_state[:, 0]
        return self.classifier(h)


def train(model, loader, optimizer, device, epochs=5):
    model.train()
    for epoch in range(1, epochs + 1):
        total, correct, count = 0.0, 0, 0
        for ids, masks, labels in loader:
            ids, masks, labels = ids.to(device), masks.to(device), labels.to(device)
            logits = model(ids, masks)
            loss = torch.nn.functional.cross_entropy(logits, labels)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            total += loss.item()
            correct += (logits.argmax(-1) == labels).sum().item()
            count += len(labels)
        print(f"epoch {epoch}/{epochs} loss={total/len(loader):.4f} acc={correct/count:.4f}")
    path = OUTPUT / "models" / "bert_relation.pt"
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)
    print(f"[OK] 模型已保存: {path}")


def main():
    parser = argparse.ArgumentParser(description="BERT 关系抽取")
    parser.add_argument("--train", type=Path)
    parser.add_argument("--predict", type=str, help="格式: 句子|头实体|尾实体")
    parser.add_argument("--model", default=BERT_MODEL)
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    ckpt = OUTPUT / "models" / "bert_relation.pt"

    if args.train:
        samples = json.loads(Path(args.train).read_text(encoding="utf-8"))
        rels = sorted({s["relation"] for s in samples})
        rel2id = {r: i for i, r in enumerate(rels)}
        model = BertRelation(args.model, len(rels)).to(device)
        loader = DataLoader(RelDataset(samples, tokenizer, rel2id), batch_size=BATCH_SIZE,
                            shuffle=True, collate_fn=collate_fn)
        train(model, loader, torch.optim.AdamW(model.parameters(), lr=LR_BERT), device, args.epochs)
        torch.save(rel2id, OUTPUT / "models" / "rel2id.json")
        return

    if not ckpt.exists():
        raise SystemExit(f"未找到模型 {ckpt}，请先 --train")
    rel2id = json.loads((OUTPUT / "models" / "rel2id.json").read_text(encoding="utf-8"))
    id2rel = {v: k for k, v in rel2id.items()}
    model = BertRelation(args.model, len(rel2id)).to(device)
    model.load_state_dict(torch.load(ckpt, map_location=device))
    model.eval()

    if args.predict:
        text, head, tail = args.predict.split("|")
        enc = tokenizer(text, f"{head}[SEP]{tail}", truncation=True,
                        max_length=MAX_LEN, return_tensors="pt")
        with torch.no_grad():
            logits = model(enc["input_ids"].to(device), enc["attention_mask"].to(device))
        print(f"预测关系: {id2rel[int(logits.argmax(-1))]}")


if __name__ == "__main__":
    main()
