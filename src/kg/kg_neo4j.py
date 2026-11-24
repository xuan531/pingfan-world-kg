#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Cypher 脚本导入 Neo4j，并提供查询与统计接口。

    pip install neo4j
    python src/kg/kg_neo4j.py --import
    python src/kg/kg_neo4j.py --stats
    python src/kg/kg_neo4j.py --query 'MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name LIMIT 10'
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import CYPHER, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER

DEFAULT_QUERIES = [
    'MATCH (a)-[r:SPOUSE]->(b) RETURN a.name AS 夫, b.name AS 妻',
    'MATCH (f)-[:FATHER_OF]->(c) RETURN f.name AS 父亲, c.name AS 子女',
    'MATCH (p {name:"孙少平"})-[r]->(q) RETURN type(r) AS 关系, q.name AS 对象',
    'MATCH (a)-[r]->(b) RETURN a.name AS 起点, type(r) AS 关系, b.name AS 终点, r.evidence AS 证据 LIMIT 20',
]


def split_statements(cypher: str) -> list[str]:
    """按分号拆分 Cypher，过滤纯注释语句。"""
    out = []
    for stmt in cypher.split(";"):
        lines = [l for l in stmt.splitlines() if l.strip() and not l.strip().startswith("//")]
        if lines:
            out.append("\n".join(lines))
    return out


class Neo4jClient:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:
            raise SystemExit("缺少依赖，请先执行: pip install neo4j") from exc
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run(self, statement: str) -> list[dict]:
        with self.driver.session() as session:
            return [dict(record) for record in session.run(statement)]

    def import_cypher(self, path: Path = CYPHER) -> int:
        statements = split_statements(Path(path).read_text(encoding="utf-8"))
        for i, stmt in enumerate(statements, 1):
            self.run(stmt)
            print(f"  [{i}/{len(statements)}] 执行完成")
        return len(statements)

    def stats(self) -> dict:
        nodes = self.run("MATCH (n) RETURN count(n) AS c")[0]["c"]
        rels = self.run("MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"]
        labels = self.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS c ORDER BY c DESC")
        return {"nodes": nodes, "relationships": rels,
                "labels": {r["label"]: r["c"] for r in labels}}


def main():
    parser = argparse.ArgumentParser(description="Neo4j 知识图谱导入与查询")
    parser.add_argument("--import", dest="do_import", action="store_true", help="导入 Cypher 脚本")
    parser.add_argument("--stats", action="store_true", help="显示图统计")
    parser.add_argument("--query", type=str, help="执行自定义 Cypher 查询")
    args = parser.parse_args()

    client = Neo4jClient()
    try:
        if args.do_import:
            n = client.import_cypher()
            print(f"[OK] 导入完成，共执行 {n} 条语句")
        if args.stats:
            print("图统计:", client.stats())
        if args.query:
            for row in client.run(args.query):
                print(row)
        if not (args.do_import or args.stats or args.query):
            print("[示例查询]")
            for q in DEFAULT_QUERIES:
                print(f"  {q}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
