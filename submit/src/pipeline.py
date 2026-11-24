#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""端到端流水线：实体抽取 → 关系抽取 → 知识图谱 → 自动评估。

    python src/pipeline.py                 # 使用已产出的 LLM 结果走完整流程
    python src/pipeline.py --use-llm       # 重新调用 LLM API 抽取（需 OPENAI_API_KEY）
    python src/pipeline.py --step kg       # 只跑知识图谱构建
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
SRC = ROOT / "src"


def run(script: str, *args: str) -> None:
    cmd = [PY, str(SRC / script), *args]
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    parser = argparse.ArgumentParser(description="知识图谱构建流水线")
    parser.add_argument("--step", choices=["all", "ner", "relation", "kg", "compare"],
                        default="all", help="要执行的阶段")
    parser.add_argument("--use-llm", action="store_true",
                        help="重新调用大模型 API 做实体/关系抽取")
    args = parser.parse_args()

    print("=" * 60)
    print("《平凡的世界》知识图谱流水线")
    print("=" * 60)

    if args.step in ("all", "ner") and args.use_llm:
        run("ner/ner_llm.py")
    if args.step in ("all", "relation") and args.use_llm:
        run("relation/relation_llm.py")

    if args.step in ("all", "kg"):
        run("kg/kg_llm.py")

    if args.step in ("all", "compare"):
        run("compare.py", "--task", "ner")
        run("compare.py", "--task", "relation")

    print("\n" + "=" * 60)
    print("流水线执行完毕。产物清单：")
    for p in [
        "data/entity_dictionary.md",
        "output/machine_readable/entities.json",
        "output/machine_readable/triples.json",
        "output/machine_readable/kg.json",
        "output/machine_readable/neo4j_import.cypher",
        "output/auto_compare_ner.md",
        "output/auto_compare_relation.md",
    ]:
        path = ROOT / p
        print(f"  {'[OK]' if path.exists() else '[--]'} {p}")
    print("=" * 60)


if __name__ == "__main__":
    main()
