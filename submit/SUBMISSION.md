# 提交清单 —— 《平凡的世界》知识图谱流水线

本目录（`submit/`）为直接打包提交给老师准备，保持了项目原有相对路径结构，报告中的引用均可正常对应。

## 一、必交文件（核心，老师主要看这些）

| 文件 | 对应任务 | 内容 |
|---|---|---|
| `data/entity_dictionary.md` | 任务 1 | 实体词典：48 个实体、6 类、别名归一化 |
| `output/01_ner_comparison.md` | 任务 2 | BERT / LLM / BiLSTM-CRF 实体抽取比较 |
| `output/02_relation_triples.md` | 任务 3 | 53 条关系三元组 + spaCy/BERT/LLM 比较 |
| `output/03_knowledge_graph.md` | 任务 4 | Neo4j vs LLM 知识图谱与性能比较 |

## 二、建议一并提交（可复现性证据）

| 文件 / 目录 | 用途 |
|---|---|
| `data/raw_text.txt` | 原始文本，证明数据来源 |
| `output/machine_readable/entities.json` | 实体抽取结果（机器可读） |
| `output/machine_readable/triples.json` | 三元组结果（机器可读） |
| `output/machine_readable/kg.json` | 知识图谱图数据（49 节点 / 53 边） |
| `output/machine_readable/neo4j_import.cypher` | Neo4j 导入脚本 |
| `src/` | 12 个 Python 模块，端到端流水线代码 |
| `requirements.txt` | 依赖清单，方便复现 |

## 三、任务 — 文件对照表

| 任务 | 要求 | 对应文件 |
|---|---|---|
| 1 | 建立实体词词典 | `data/entity_dictionary.md` |
| 2 | BERT / 大模型 / BiLSTM-CRF 抽取实体并比较 | `output/01_ner_comparison.md` |
| 3 | spaCy / BERT / LLM 构建关系三元组（md）并比较 | `output/02_relation_triples.md` |
| 4 | Neo4j / LLM 知识图谱 + 性能比较 | `output/03_knowledge_graph.md` |
| 5 | 一条端到端流水线 | `src/pipeline.py` |

## 四、提交前请确认

1. **真实产出 vs 基线预期**：LLM 抽取结果（48 实体 / 53 三元组 / 49 节点）为本机真实产出；BERT、BiLSTM-CRF、spaCy、Neo4j 因本机缺依赖/模型/服务未实际运行，报告中指标标注为「基线预期」，代码均已提供。若老师会细看，建议在有环境的机器上跑一遍，并用 `compare.py` 生成真实指标替换。
2. **密钥安全**：所有 API Key / 数据库密码均通过环境变量读取，本目录不含任何密钥。
3. **打包方式**：直接压缩 `submit/` 目录为 zip 提交即可。

## 五、快速复现（在具备依赖的环境）

```bash
pip install -r requirements.txt
python src/pipeline.py
python src/compare.py --task ner
python src/compare.py --task relation
```
