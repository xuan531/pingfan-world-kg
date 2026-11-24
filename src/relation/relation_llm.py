#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用大模型零样本抽取关系三元组（OpenAI 兼容接口）。

    export OPENAI_API_KEY=sk-xxx
    python src/relation/relation_llm.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, MR, RAW_TEXT

RELATIONS = {
    "SPOUSE": "配偶", "LOVER": "恋人/爱慕", "PROPOSE": "表白", "REJECT": "拒绝",
    "SIBLING": "兄弟姐妹", "FATHER_OF": "父亲", "FRIEND": "朋友", "CLASSMATE": "同学",
    "REVEAL": "说破/揭露", "INTRODUCE": "介绍婚事", "HELP": "帮助", "RECOGNIZE": "承认",
    "OPPOSE": "反对", "LEAD": "领导", "ORGANIZE": "组织", "PARTICIPATE_IN": "参与",
    "INFORM": "告知", "PROMISE": "相约", "MEET": "邂逅", "RETURN_TO": "回到",
    "ATTEND": "出席", "STUDY_AT": "就读于", "WORK_AT": "工作于", "FROM": "来自",
    "LOCATED_AT": "发生于", "MOTIVATE": "驱动", "ACHIEVE": "成为/获得",
    "DIE_IN": "牺牲于", "GRIEVE": "悲痛于", "INJURED_IN": "受伤于",
    "DIAGNOSE_WITH": "确诊", "FUNDS": "出资",
}

SYSTEM_PROMPT = """你是一个中文关系抽取专家。请从文本中抽取关系三元组（头实体，关系，尾实体）。

允许的关系标签（只能使用这些英文标签）：
""" + "；".join(f"{k}({v})" for k, v in RELATIONS.items()) + """

要求：
1. 头尾实体必须是文本中出现或可明确归一的实体（人物用标准名，如“少平”→“孙少平”）。
2. 只抽取文本明确表达或强蕴含的关系，不得编造。
3. 每条三元组必须给出 evidence（原文证据短语）和 section（第一部/第二部概要/第三部）。
4. 只输出 JSON 数组，不要解释文字，不要 Markdown 代码块。

输出格式：
{"head": "孙少平", "relation": "STUDY_AT", "tail": "原西县高中", "evidence": "到原西县高中读书", "section": "第一部"}
"""


def build_prompt(text: str) -> str:
    return f"待抽取文本：\n\n{text}\n\n请按系统要求输出关系三元组 JSON 数组。"


def call_llm(prompt: str, model: str = LLM_MODEL) -> str:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("缺少依赖，请先执行: pip install openai") from exc
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return resp.choices[0].message.content or ""


def parse_response(content: str) -> list[dict]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.M)
    start, end = cleaned.find("["), cleaned.rfind("]")
    if start < 0 or end < 0:
        raise ValueError(f"未找到 JSON 数组: {content[:200]}")
    data = json.loads(cleaned[start:end + 1])
    valid = [d for d in data if d.get("relation") in RELATIONS]
    return valid


def main():
    parser = argparse.ArgumentParser(description="LLM 零样本关系抽取")
    parser.add_argument("--input", type=Path, default=RAW_TEXT)
    parser.add_argument("--output", type=Path, default=MR / "llm_triples.json")
    parser.add_argument("--model", default=LLM_MODEL)
    args = parser.parse_args()

    if not LLM_API_KEY:
        print("[提示] 未设置 OPENAI_API_KEY，跳过真实 API 调用。")
        print("       本项目已产出结果：output/machine_readable/triples.json")
        return

    text = args.input.read_text(encoding="utf-8")
    triples = parse_response(call_llm(build_prompt(text), args.model))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(triples, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 抽取 {len(triples)} 条三元组 → {args.output}")


if __name__ == "__main__":
    main()
