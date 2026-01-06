"""Minimal migrations engine: generate plan files, apply to SQLite (initial).

Writes a snapshot and a simple JSON plan, applies to SQLite via DDL.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List


def write_snapshot(snapshot_path: Path, graph: Dict[str, Any]) -> None:
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "enums": graph.get("enums", {}),
        "models": {k: {"table": v.get("table"), "fields": list(v.get("fields", {}).keys())} for k, v in graph.get("models", {}).items()},
        "relations": graph.get("relations", []),
    }
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))


def write_plan(plan_path: Path, ops: List[Dict[str, Any]]) -> None:
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps({"ops": ops}, ensure_ascii=False, indent=2))


def _sqlite_type(field: Dict[str, Any]) -> str:
    t = field.get("type")
    params = field.get("params", [])
    kwargs = field.get("kwargs", {})

    if t == "AutoField":
        return "INTEGER PRIMARY KEY AUTOINCREMENT"
    if t == "ForeignKey":
        return "INTEGER"
    if t == "DecimalField":
        p, s = (0, 0)
        if params:
            if isinstance(params[0], tuple):
                p, s = params[0]
            elif len(params) >= 2:
                p, s = int(params[0]), int(params[1])
        return f"NUMERIC({p},{s})"
    if t == "DateTimeField":
        return "TEXT"
    if t == "EnumField":
        return "TEXT"
    if t == "BooleanField" or t == "bool":
        return "INTEGER"
    if t == "CharField" or t == "string":
        maxlen = (params[0] if params else 255)
        try:
            maxlen = int(maxlen)
        except Exception:
            maxlen = 255
        return f"VARCHAR({maxlen})"
    if t == "IntegerField" or t == "int":
        return "INTEGER"
    return "TEXT"


def apply_sqlite(dsn: str, ops: List[Dict[str, Any]], graph: Dict[str, Any]) -> None:
    conn = sqlite3.connect(dsn)
    try:
        cur = conn.cursor()
        # Build CREATE TABLE statements including enum checks when possible
        for op in ops:
            if op["op"] == "create_model":
                table = op["table"]
                cols: List[str] = []
                checks: List[str] = []
                for f in op.get("fields", []):
                    coltype = _sqlite_type(f)
                    col = f["name"]
                    cols.append(f"{col} {coltype}")
                    if f.get("type") == "EnumField":
                        enum_name = None
                        if f.get("params"):
                            enum_name = str(f["params"][0])
                        values = graph.get("enums", {}).get(enum_name or "", [])
                        if values:
                            allowed = ",".join([f"'" + v[1] + "'" for v in values])
                            checks.append(f"CHECK ({col} IN ({allowed}))")
                ddl = f"CREATE TABLE IF NOT EXISTS {table} (" + ", ".join(cols + checks) + ")"
                cur.execute(ddl)

            elif op["op"] == "add_fk":
                # SQLite needs FK enabled via PRAGMA; adding FK after create requires table rebuild.
                # Minimal approach: ensure PRAGMA and rely on table having FK column. Skip alter here.
                cur.execute("PRAGMA foreign_keys = ON")
                # TODO: rebuild table with FK constraint if needed (later iteration).

            elif op["op"] == "create_enum":
                # No separate enum storage in sqlite for now; handled via CHECK at create_model.
                pass

        conn.commit()
    finally:
        conn.close()
