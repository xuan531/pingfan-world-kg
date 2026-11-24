#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全局配置：路径、模型、超参数、环境变量。"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
MR = OUTPUT / "machine_readable"

RAW_TEXT = DATA / "raw_text.txt"
ENTITY_DICT = DATA / "entity_dictionary.md"
ENTITIES_JSON = MR / "entities.json"
TRIPLES_JSON = MR / "triples.json"
KG_JSON = MR / "kg.json"
CYPHER = MR / "neo4j_import.cypher"

# 实体类型体系
ENTITY_TYPES = ["PERSON", "LOCATION", "ORGANIZATION", "TIME", "EVENT", "CONCEPT"]

# BIO 标签
BIO_TAGS = ["O"] + [f"{p}-{t}" for t in ENTITY_TYPES for p in ("B", "I")]
TAG2ID = {tag: i for i, tag in enumerate(BIO_TAGS)}
ID2TAG = {i: tag for tag, i in TAG2ID.items()}

# 模型
BERT_MODEL = os.getenv("BERT_MODEL", "bert-base-chinese")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
SPACY_MODEL = os.getenv("SPACY_MODEL", "zh_core_web_sm")

# Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password123")

# 训练超参数
MAX_LEN = 256
BATCH_SIZE = 16
LR_BERT = 2e-5
LR_BILSTM = 1e-3
EPOCHS_BERT = 5
EPOCHS_BILSTM = 20
EMBED_DIM = 128
HIDDEN_DIM = 256
DROPOUT = 0.5
SEED = 42


def ensure_dirs() -> None:
    for p in (DATA, OUTPUT, MR):
        p.mkdir(parents=True, exist_ok=True)
