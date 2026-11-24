#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动汇总各方法抽取结果，按金标准计算 P/R/F1，输出 Markdown 比较表。

    python src/compare.py --task ner
    python src/compare.py --task relation
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ENTITIES_JSON, MR, OUTPUT, TRIPLES_JSON


def load(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def prf(pred: set, gold: set) -> dict:
    tp = len(pred & gold)
    fp = len(pred - gold)
    fn = len(gold - pred)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"n": len(pred), "p": round(p, 4), "r": round(r, 4), "f1": round(f, 4)}


def gold_entities() -> set:
    data = load(ENTITIES_JSON)
    return {e["standard_name"] for e in data["entities"]} if data else set()


def gold_triples() -> set:
    data = load(TRIPLES_JSON)
    return {(t["head"], t["relation"], t["tail"]) for t in data["triples"]} if data else set()


def entity_set(path: Path) -> set:
    data = load(path)
    if not data:
        return set()
    if isinstance(data, dict) and "entities" in data:
        data = data["entities"]
    return {e.get("standard_name") or e.get("label") for e in data if isinstance(e, dict)}


def triple_set(path: Path) -> set:
    data = load(path)
    if not data:
        return set()
    if isinstance(data, dict) and "triples" in data:
        data = data["triples"]
    return {(t["head"], t["relation"], t["tail"]) for t in data if isinstance(t, dict)}


def report_ner() -> str:
    gold = gold_entities()
    rows = []
    candidates = [
        ("LLM（已校验 gold）", ENTITIES_JSON),
        ("LLM 原始输出", MR / "llm_entities.json"),
        ("BERT-CRF", MR / "bert_entities.json"),
        ("BiLSTM-CRF", MR / "bilstm_entities.json"),
    ]
    for name, path in candidates:
        if path == ENTITIES_JSON:
            rows.append(f"| {name} | {len(gold)} | 1.0000 | 1.0000 | 1.0000 |")
            continue
        pred = entity_set(path)
        if not pred:
            rows.append(f"| {name} | — | 未运行 | 未运行 | 未运行 |")
            continue
        m = prf(pred, gold)
        rows.append(f"| {name} | {m['n']} | {m['p']} | {m['r']} | {m['f1']} |")
    return ("## 实体抽取比较（自动计算）\n\n"
            "| 方法 | 实体数 | Precision | Recall | F1 |\n|---|---:|---:|---:|---:|\n"
            + "\n".join(rows) + "\n\n> 金标准: entities.json；未运行的方法显示“未运行”。\n")


def report_relation() -> str:
    gold = gold_triples()
    rows = []
    candidates = [
        ("LLM（已校验 gold）", TRIPLES_JSON),
        ("LLM 原始输出", MR / "llm_triples.json"),
        ("BERT", MR / "bert_triples.json"),
        ("spaCy 规则", MR / "spacy_triples.json"),
    ]
    for name, path in candidates:
        if path == TRIPLES_JSON:
            rows.append(f"| {name} | {len(gold)} | 1.0000 | 1.0000 | 1.0000 |")
            continue
        pred = triple_set(path)
        if not pred:
            rows.append(f"| {name} | — | 未运行 | 未运行 | 未运行 |")
            continue
        m = prf(pred, gold)
        rows.append(f"| {name} | {m['n']} | {m['p']} | {m['r']} | {m['f1']} |")
    return ("## 关系抽取比较（自动计算）\n\n"
            "| 方法 | 三元组数 | Precision | Recall | F1 |\n|---|---:|---:|---:|---:|\n"
            + "\n".join(rows) + "\n\n> 金标准: triples.json；匹配依据为 (head, relation, tail) 完全一致。\n")


def main():
    parser = argparse.ArgumentParser(description="抽取方法比较分析")
    parser.add_argument("--task", choices=["ner", "relation"], required=True)
    args = parser.parse_args()
    text = report_ner() if args.task == "ner" else report_relation()
    out = OUTPUT / f"auto_compare_{args.task}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"[OK] 已写入 {out}")


if __name__ == "__main__":
    main()
