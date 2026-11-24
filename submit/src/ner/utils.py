#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NER 共用工具：BIO 数据读取、实体还原、span 级 P/R/F1 评估。"""
from __future__ import annotations

from pathlib import Path


def load_bio(path: str | Path) -> list[tuple[list[str], list[str]]]:
    """读取 CoNLL/BIO 文件：每行为「字<TAB>标签」，空行分隔句子。"""
    samples, chars, tags = [], [], []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                if chars:
                    samples.append((chars, tags))
                    chars, tags = [], []
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            chars.append(parts[0])
            tags.append(parts[-1])
    if chars:
        samples.append((chars, tags))
    return samples


def extract_entities(tag_ids: list[int], id2tag: dict[int, str]) -> list[tuple[str, int, int]]:
    """把 BIO/BILOU 标签序列还原为 (类型, 起始, 结束) 实体集合。"""
    entities, cur = [], None
    for i, tid in enumerate(tag_ids):
        if tid == -100:
            continue
        tag = id2tag.get(int(tid), "O")
        if tag == "O":
            if cur:
                entities.append(cur)
                cur = None
            continue
        prefix, _, etype = tag.partition("-")
        if prefix == "B" or cur is None or etype != cur[0]:
            if cur:
                entities.append(cur)
            cur = (etype, i, i)
        elif prefix in ("I", "E", "L"):
            cur = (cur[0], cur[1], i)
        elif prefix == "S":
            entities.append((etype, i, i))
            cur = None
    if cur:
        entities.append(cur)
    return entities


def evaluate_spans(preds: list, golds: list, id2tag: dict[int, str]) -> dict:
    """按实体 span 计算 micro P/R/F1。preds/golds 为批次标签 id 列表。"""
    tp = fp = fn = 0
    for p_seq, g_seq in zip(preds, golds):
        p_set = set(extract_entities(p_seq, id2tag))
        g_set = set(extract_entities(g_seq, id2tag))
        tp += len(p_set & g_set)
        fp += len(p_set - g_set)
        fn += len(g_set - p_set)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4),
            "f1": round(f1, 4), "tp": tp, "fp": fp, "fn": fn}
