#!/usr/bin/env python3
"""Execute every management query and reconcile SQL output to source controls."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
summary = json.loads((ROOT / "analysis" / "executive_summary.json").read_text())["summary"]
sql = (ROOT / "sql" / "02_management_questions.sql").read_text()
queries = []
statement = ""

with sqlite3.connect(ROOT / "data" / "clean" / "morrowfield_analytics.sqlite") as connection:
    for line in sql.splitlines(keepends=True):
        statement += line
        if not sqlite3.complete_statement(statement):
            continue
        current = statement.strip()
        if current:
            cursor = connection.execute(current)
            rows = cursor.fetchall()
            columns = [item[0] for item in cursor.description]
            queries.append({"query": len(queries) + 1, "rows": len(rows), "columns": columns})
            if len(queries) == 1:
                first = dict(zip(columns, rows[0]))
                for key in ["net_sales", "gross_profit", "estimated_lost_sales"]:
                    if abs(first[key] - summary[key]) > .02:
                        raise ValueError(f"SQL executive result disagrees with control: {key}")
            if len(queries) == 10 and any(row[1] != 0 for row in rows):
                raise ValueError("SQL source-integrity query returned an exception")
        statement = ""

if len(queries) != 10:
    raise ValueError(f"Expected ten management queries, found {len(queries)}")

result = {"passed": True, "query_count": len(queries), "queries": queries}
(ROOT / "qa" / "sql_validation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"status": "ok", "queries": len(queries), "integrity_exceptions": 0}))
