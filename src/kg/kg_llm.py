#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 LLM 抽取结果（entities.json + triples.json）构建知识图谱数据，
并生成可直接导入 Neo4j 的 Cypher 脚本。

这一步对应任务 4 中的「用 LLM 生成知识图谱」：
  - kg.json            : 图结构数据（节点 + 边 + 统计），供前端/图分析使用
  - neo4j_import.cypher: Neo4j 导入脚本（MERGE 幂等）

运行: python src/kg/kg_llm.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "output" / "machine_readable"

NODE_LABELS = ["PERSON", "LOCATION", "ORGANIZATION", "TIME", "EVENT", "CONCEPT"]


def load_json(name: str) -> dict:
    with (DATA / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def esc(value) -> str:
    """转义 Cypher 字符串中的特殊字符。"""
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def build_kg() -> dict:
    entities = load_json("entities.json")["entities"]
    triples = load_json("triples.json")["triples"]

    nodes = [
        {
            "id": e["id"],
            "label": e["standard_name"],
            "type": e["type"],
            "aliases": e["aliases"],
            "description": e["description"],
            "frequency": e.get("frequency", 1),
            "sections": e.get("sections", []),
        }
        for e in entities
    ]

    # 建立「标准名 + 别名」→ id 映射，避免「矿山/煤矿」等别名被重复建成节点
    id_of = {}
    for n in nodes:
        id_of[n["label"]] = n["id"]
        for alias in n["aliases"]:
            id_of.setdefault(alias, n["id"])

    # 抽取阶段发现但词典未收录的实体（如「肺癌」），自动补为 CONCEPT 节点
    extra = sorted({t[k] for t in triples for k in ("head", "tail") if t[k] not in id_of})
    for i, name in enumerate(extra, start=len(nodes) + 1):
        new_id = f"E{i:02d}"
        nodes.append(
            {
                "id": new_id,
                "label": name,
                "type": "CONCEPT",
                "aliases": [],
                "description": "抽取过程中新增的实体（LLM 发现）",
                "frequency": 1,
                "sections": [],
            }
        )
        id_of[name] = new_id

    label_of_id = {n["id"]: n["label"] for n in nodes}
    edges = [
        {
            "id": t["id"],
            "source": id_of[t["head"]],
            "target": id_of[t["tail"]],
            "head": label_of_id[id_of[t["head"]]],
            "tail": label_of_id[id_of[t["tail"]]],
            "relation": t["relation"],
            "section": t["section"],
            "evidence": t["evidence"],
        }
        for t in triples
    ]

    stats = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_types": dict(Counter(n["type"] for n in nodes)),
        "relation_counts": dict(Counter(e["relation"] for e in edges)),
        "sections": dict(Counter(e["section"] for e in edges)),
    }
    return {"nodes": nodes, "edges": edges, "stats": stats}


def write_cypher(kg: dict, path: Path) -> None:
    lines = [
        "// ============================================================",
        "// 《平凡的世界》知识图谱 —— Neo4j 导入脚本",
        "// 由 LLM 抽取结果自动生成（entities.json + triples.json）",
        "// 用法: cypher-shell -u neo4j -p <password> -f neo4j_import.cypher",
        "// ============================================================",
        "",
        "// 1. 唯一性约束（幂等）",
    ]
    for label in NODE_LABELS:
        lines.append(
            f"CREATE CONSTRAINT {label}_name IF NOT EXISTS "
            f"FOR (n:{label}) REQUIRE n.name IS UNIQUE;"
        )

    lines += ["", "// 2. 创建节点（MERGE 幂等，可重复执行）"]
    for n in kg["nodes"]:
        aliases = ", ".join(f'"{esc(a)}"' for a in n["aliases"])
        lines.append(
            f'MERGE (n:{n["type"]} {{name: "{esc(n["label"])}"}}) '
            f'ON CREATE SET n.id = "{n["id"]}", '
            f'n.aliases = [{aliases}], '
            f'n.description = "{esc(n["description"])}", '
            f'n.frequency = {int(n["frequency"])};'
        )

    lines += ["", "// 3. 创建关系（MERGE 幂等，附带原文证据）"]
    for e in kg["edges"]:
        lines.append(
            f'MATCH (a {{name: "{esc(e["head"])}"}}), (b {{name: "{esc(e["tail"])}"}}) '
            f'MERGE (a)-[r:{e["relation"]} {{id: "{e["id"]}"}}]->(b) '
            f'ON CREATE SET r.evidence = "{esc(e["evidence"])}", '
            f'r.section = "{esc(e["section"])}";'
        )

    lines += [
        "",
        "// 4. 常用查询示例（取消注释即可运行）",
        '// MATCH (p:PERSON)-[r:SPOUSE]->(q) RETURN p.name, q.name;',
        '// MATCH (p:PERSON)-[r:FATHER_OF]->(c) RETURN p.name, c.name;',
        '// MATCH (p:PERSON)-[r]->(q) WHERE p.name = "孙少平" RETURN q.name, type(r);',
        '// MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name, r.evidence LIMIT 20;',
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    kg = build_kg()
    (DATA / "kg.json").write_text(
        json.dumps(kg, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_cypher(kg, DATA / "neo4j_import.cypher")
    s = kg["stats"]
    print(
        f"[OK] kg.json / neo4j_import.cypher 已生成: "
        f"{s['node_count']} 节点, {s['edge_count']} 关系, "
        f"{len(s['relation_counts'])} 种关系类型"
    )
    print("节点类型:", s["node_types"])


if __name__ == "__main__":
    main()
