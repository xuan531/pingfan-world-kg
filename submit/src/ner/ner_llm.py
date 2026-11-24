#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用大模型（OpenAI 兼容接口）零样本抽取实体。

设置环境变量后可直接运行：
    export OPENAI_API_KEY=sk-xxx
    export OPENAI_BASE_URL=https://api.openai.com/v1   # 或其他兼容接口
    python src/ner/ner_llm.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import ENTITY_TYPES, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, MR, RAW_TEXT

SYSTEM_PROMPT = """你是一个中文命名实体识别专家。请从用户提供的文本中抽取以下六类实体：
PERSON(人物)、LOCATION(地点/场所)、ORGANIZATION(组织/机构)、TIME(时间)、EVENT(事件)、CONCEPT(概念/制度)。

要求：
1. 识别别名与简称，并将其归一化到标准名（例如“少平”→“孙少平”，“矿山”→“煤矿”）。
2. 同一实体只输出一次，aliases 列出文中出现过的所有称谓。
3. evidence 填写原文中能证明该实体的短语，不得编造。
4. 只输出 JSON 数组，不要输出解释文字、不要使用 Markdown 代码块。

输出格式（每个元素）：
{"standard_name": "孙少平", "type": "PERSON", "aliases": ["少平"], "evidence": "孙少平到原西县高中读书"}
"""


def build_prompt(text: str) -> str:
    types = "、".join(ENTITY_TYPES)
    return f"待抽取文本（实体类型：{types}）：\n\n{text}\n\n请按系统要求输出 JSON 数组。"


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
    """清洗模型输出并解析为 JSON 列表。"""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.M)
    start, end = cleaned.find("["), cleaned.rfind("]")
    if start < 0 or end < 0:
        raise ValueError(f"模型输出中未找到 JSON 数组: {content[:200]}")
    data = json.loads(cleaned[start:end + 1])
    if not isinstance(data, list):
        raise ValueError("模型输出不是 JSON 数组")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM 零样本实体抽取")
    parser.add_argument("--input", type=Path, default=RAW_TEXT)
    parser.add_argument("--output", type=Path, default=MR / "llm_entities.json")
    parser.add_argument("--model", default=LLM_MODEL)
    args = parser.parse_args()

    if not LLM_API_KEY:
        print("[提示] 未设置 OPENAI_API_KEY，跳过真实 API 调用。")
        print("       本项目已产出 LLM 抽取结果：output/machine_readable/entities.json")
        return

    text = args.input.read_text(encoding="utf-8")
    raw = call_llm(build_prompt(text), args.model)
    entities = parse_response(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(entities, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 抽取 {len(entities)} 个实体 → {args.output}")


if __name__ == "__main__":
    main()
