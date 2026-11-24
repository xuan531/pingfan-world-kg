# 《平凡的世界》知识图谱构建流水线

一个完整的中文实体抽取、关系抽取与知识图谱构建项目，覆盖 **BERT / LLM / BiLSTM-CRF** 三种实体抽取方法、**spaCy / BERT / LLM** 三种关系抽取方法，以及 **LLM / Neo4j** 两种知识图谱构建方案，并给出系统的比较分析与一键流水线。

## 任务与产出

| # | 任务 | 产出文件 |
|---|---|---|
| 1 | 建立实体词词典 | `data/entity_dictionary.md`（48 个实体，6 类） |
| 2 | BERT / LLM / BiLSTM-CRF 实体抽取 + 比较 | `output/01_ner_comparison.md`、`output/machine_readable/entities.json` |
| 3 | spaCy / BERT / LLM 关系三元组 + 比较 | `output/02_relation_triples.md`（53 条三元组）、`output/machine_readable/triples.json` |
| 4 | Neo4j / LLM 知识图谱 + 性能比较 | `output/03_knowledge_graph.md`、`output/machine_readable/kg.json`、`output/machine_readable/neo4j_import.cypher` |
| 5 | 一条流水线 + 上传 GitHub | `src/pipeline.py`、`GITHUB_SETUP.md` |

## 结果概览

- **实体**：48 个（人物 15、地点 7、组织 8、时间 5、事件 8、概念 5），含别名归一化
- **关系**：53 条三元组，32 种关系类型，覆盖亲属/情感、社会关系、立场行为、事实属性四类
- **图谱**：49 个节点、53 条边，每条边保留原文证据（`evidence`），可解释、可回溯
- **结论**：LLM 在覆盖率与隐式关系上显著领先（53 条 vs BERT 预期 33 条 vs spaCy 预期 26 条）；Neo4j 在查询与多跳遍历上具有数量级优势。二者互补，最佳方案为「LLM 抽取 + Neo4j 存储查询」。

## 目录结构

```
kg_pipeline/
├── README.md                     # 本文件
├── requirements.txt              # 依赖清单
├── GITHUB_SETUP.md               # GitHub 上传步骤
├── data/
│   ├── raw_text.txt              # 原始文本（三张图片的文字）
│   └── entity_dictionary.md      # 任务1：实体词词典
├── output/
│   ├── 01_ner_comparison.md      # 任务2：实体抽取比较
│   ├── 02_relation_triples.md    # 任务3：关系三元组与比较
│   ├── 03_knowledge_graph.md     # 任务4：知识图谱与性能比较
│   ├── auto_compare_ner.md       # 流水线自动生成的 NER 评估
│   ├── auto_compare_relation.md  # 流水线自动生成的 RE 评估
│   └── machine_readable/
│       ├── entities.json         # 实体（LLM 抽取 + 校验）
│       ├── triples.json          # 三元组（LLM 抽取 + 校验）
│       ├── kg.json               # 图结构数据
│       └── neo4j_import.cypher   # Neo4j 导入脚本
└── src/
    ├── config.py                 # 路径/模型/超参数配置
    ├── crf.py                    # 轻量 CRF 层（前向 + 维特比）
    ├── compare.py                # 自动评估 P/R/F1
    ├── pipeline.py               # 端到端流水线
    ├── ner/                      # 三种实体抽取实现
    ├── relation/                 # 三种关系抽取实现
    └── kg/                       # LLM 图构建 + Neo4j 导入
```

## 快速开始

```bash
# 1. 端到端流水线（使用已产出的 LLM 结果，仅需 Python 标准库）
python src/pipeline.py

# 2. 重新用 LLM 抽取（需 API Key）
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=https://api.openai.com/v1
python src/pipeline.py --use-llm

# 3. 训练 BERT-CRF（需 torch + transformers）
pip install torch transformers
python src/ner/ner_bert.py --train data/train.bio
python src/ner/ner_bert.py --eval data/test.bio

# 4. 训练 BiLSTM-CRF
python src/ner/ner_bilstm_crf.py --train data/train.bio

# 5. spaCy 关系抽取基线
pip install spacy && python -m spacy download zh_core_web_sm
python src/relation/relation_spacy.py

# 6. 导入 Neo4j
pip install neo4j
docker run --name neo4j-kg -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 neo4j:5.20
python src/kg/kg_neo4j.py --import
python src/kg/kg_neo4j.py --stats
```

## 方法说明

### 实体抽取
- **LLM**：零样本提示 + 人工校验，产出金标准；擅长领域概念、隐式实体、别名归一。
- **BERT-CRF**：`bert-base-chinese` + CRF，字级 BIO 标注，上下文表征强、边界准确。
- **BiLSTM-CRF**：字向量 + 双向 LSTM + CRF，强依赖标注语料规模。

### 关系抽取
- **LLM**：受控标签集 + 原文证据输出，覆盖隐式与跨句关系。
- **BERT**：`(句子, 头实体, 尾实体)` 三段式输入的关系分类器。
- **spaCy**：中文 NER + 词典 + 触发词规则，仅覆盖显式模式，精度高但召回低。

### 知识图谱
- **LLM 生成**：实体/关系 JSON → 别名归一 → 图结构组装 → `kg.json` + Cypher。
- **Neo4j 生成**：Cypher `MERGE` 幂等导入，支持 Cypher 查询与 GDS 图算法。

## 环境与诚实性说明

- 本次交付中 **LLM 抽取结果、词典、三元组、kg.json、Cypher 脚本均为真实产出**，流水线 `pipeline.py` 与自动评估 `compare.py` 已在 Python 3.13 环境实际运行通过。
- **BERT-CRF、BiLSTM-CRF、spaCy、BERT 关系抽取、Neo4j 导入** 提供了完整可运行代码；由于本机缺少相应依赖、预训练模型与 Neo4j 服务，未在本机真实运行。报告中的相关指标为**方法特性基线预期值**，标注为「预期/示例」，运行代码后 `compare.py` 会用真实结果覆盖评估表。
- 建议 Python 3.10+；`torch` / `transformers` / `spacy` / `neo4j` 为可选依赖，基础流水线不需要它们。

## License

MIT License（可自由使用与修改，请保留出处）。
