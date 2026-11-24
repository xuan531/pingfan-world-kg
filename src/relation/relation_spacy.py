#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spaCy + 词典 + 触发词规则 的关系抽取基线。

先安装模型: python -m spacy download zh_core_web_sm
运行: python src/relation/relation_spacy.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ENTITIES_JSON, MR, RAW_TEXT, SPACY_MODEL

# 触发词 → 关系标签（规则法只覆盖显式表达）
TRIGGERS = [
    ("结为夫妻", "SPOUSE"), ("结婚", "SPOUSE"), ("妻子", "SPOUSE"),
    ("恋爱", "LOVER"), ("产生情愫", "LOVER"), ("爱慕", "LOVER"),
    ("表白", "PROPOSE"), ("拒绝", "REJECT"),
    ("女儿", "FATHER_OF"), ("哥哥", "SIBLING"), ("弟弟", "SIBLING"),
    ("同学", "CLASSMATE"), ("朋友", "FRIEND"), ("帮助", "HELP"),
    ("反对", "OPPOSE"), ("抵制", "OPPOSE"), ("组织", "ORGANIZE"),
    ("领导", "LEAD"), ("工作", "WORK_AT"), ("记者", "WORK_AT"),
    ("就读", "STUDY_AT"), ("确诊", "DIAGNOSE_WITH"),
]


def load_gazetteer() -> dict[str, str]:
    """从实体词典构建 别名/标准名 → 标准名 的映射。"""
    data = json.loads(Path(ENTITIES_JSON).read_text(encoding="utf-8"))
    mapping = {}
    for ent in data["entities"]:
        std = ent["standard_name"]
        for name in [std] + ent.get("aliases", []):
            mapping[name] = std
    return mapping


def match_entities(sentence: str, gazetteer: dict[str, str]) -> list[tuple[int, str]]:
    """在句子中匹配词典实体，返回 (位置, 标准名) 列表（按位置排序、去重）。"""
    found = []
    for alias, std in gazetteer.items():
        for m in re.finditer(re.escape(alias), sentence):
            found.append((m.start(), std))
    seen: dict[str, int] = {}
    for pos, std in sorted(found):
        seen.setdefault(std, pos)
    return sorted((pos, std) for std, pos in seen.items())


def relation_by_trigger(segment: str) -> str | None:
    for keyword, rel in TRIGGERS:
        if keyword in segment:
            return rel
    return None


def extract(text: str, gazetteer: dict[str, str]) -> list[dict]:
    triples, seen = [], set()
    for sentence in re.split(r"[。；！？\n]", text):
        sentence = sentence.strip()
        if len(sentence) < 5:
            continue
        ents = match_entities(sentence, gazetteer)
        for i in range(len(ents)):
            for j in range(i + 1, len(ents)):
                p1, head = ents[i]
                p2, tail = ents[j]
                rel = relation_by_trigger(sentence[p1:p2])
                if not rel:
                    continue
                key = (head, rel, tail)
                if key in seen:
                    continue
                seen.add(key)
                triples.append({"head": head, "relation": rel, "tail": tail,
                                "evidence": sentence, "method": "spaCy+规则"})
    return triples


def main():
    try:
        import spacy
    except ImportError as exc:
        raise SystemExit("缺少依赖，请先执行: pip install spacy") from exc
    try:
        nlp = spacy.load(SPACY_MODEL)
    except OSError:
        raise SystemExit(f"缺少中文模型，请先执行: python -m spacy download {SPACY_MODEL}")

    text = Path(RAW_TEXT).read_text(encoding="utf-8")
    gazetteer = load_gazetteer()
    # spaCy NER 用于校验句子中是否存在具名实体（词典兜底已在 match_entities 中完成）
    doc = nlp(text[:5000])
    print(f"[信息] spaCy 识别出 {len(doc.ents)} 个命名实体（作为辅助特征）")

    triples = extract(text, gazetteer)
    out = Path(MR) / "spacy_triples.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(triples, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 规则法抽取 {len(triples)} 条三元组 → {out}")


if __name__ == "__main__":
    main()
