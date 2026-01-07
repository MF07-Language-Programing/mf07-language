"""Minimal parser for Django-like Model DSL inside .mp files.

Parses constructs:
- enum Name { A, B, C }
- enum Name: VALUES = "VALUES" style also supported
- model Name extends Model {\n  field = Type(args...)\n  table = "name"\n}

Example fields:
- id = AutoField()
- user = ForeignKey(User)
- status = EnumField(OrderStatus, default=OrderStatus.PENDING)
- total = DecimalField(10, 2)
- created_at = DateTimeField(auto_now_add=true)

Returns a simple schema dict with models, fields, enums, relations.
"""

from __future__ import annotations
import re
from typing import Any, Dict, List, Tuple


_ENUM_BLOCK_RE = re.compile(r"enum\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\{(?P<body>.*?)\}", re.DOTALL)
_MODEL_RE = re.compile(r"model\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+extends\s+(?P<base>Model|BaseModel)\s*\{(?P<body>.*?)\}", re.DOTALL)


def _parse_enum_block(body: str) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    # Accept lines like: NAME, or NAME = "VALUE"
    for raw in re.split(r"[,\n]", body):
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)(\s*=\s*\"(?P<val>[^\"]+)\")?$", line)
        if not m:
            continue
        key = m.group("key")
        val = m.group("val") or key
        items.append((key, val))
    return items


def _parse_model_body(body: str) -> Dict[str, Any]:
    fields: Dict[str, Any] = {}
    table_name: str | None = None

    # Split by lines and remove comments
    lines = [re.sub(r"//.*$", "", ln).strip() for ln in body.splitlines()]
    for ln in lines:
        if not ln:
            continue
        # table = "orders"
        mt = re.match(r"^table\s*=\s*\"(?P<t>[A-Za-z0-9_]+)\"\s*;?$", ln)
        if mt:
            table_name = mt.group("t")
            continue

        # name = Type(args)
        m = re.match(r"^(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<type>[A-Za-z_][A-Za-z0-9_]*)\s*\((?P<args>[^)]*)\)\s*;?$", ln)
        if not m:
            continue
        fname = m.group("name")
        ftype = m.group("type")
        args = m.group("args").strip()

        field: Dict[str, Any] = {"name": fname, "type": ftype, "params": [], "kwargs": {}}

        # args can be positional and keyword-like: key=value or true/false
        if args:
            parts = [p.strip() for p in re.split(r",", args) if p.strip()]
            for p in parts:
                kv = re.match(r"^(?P<k>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<v>.+)$", p)
                if kv:
                    k = kv.group("k")
                    v = kv.group("v").strip()
                    field["kwargs"][k] = _normalize_value(v)
                else:
                    field["params"].append(_normalize_value(p))

        fields[fname] = field

    return {"table": table_name, "fields": fields}


def _normalize_value(v: str) -> Any:
    v = v.strip()
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if re.match(r"^\d+$", v):
        try:
            return int(v)
        except Exception:
            return v
    if re.match(r"^\d+\s*,\s*\d+$", v):
        # "10, 2" positional decimal params handled separately
        return tuple(int(x.strip()) for x in v.split(","))
    m = re.match(r"^\"(?P<s>.*)\"$", v)
    if m:
        return m.group("s")
    return v


def parse_models(source: str) -> Dict[str, Any]:
    """Parse a .mp source containing enums and models. Returns schema dict:
    { "enums": {name: [(key,value), ...]}, "models": {name: {table, fields}}, "relations": [ ... ] }
    Relations are inferred from ForeignKey/User etc.
    """
    result = {"enums": {}, "models": {}, "relations": []}

    # Enums
    for em in _ENUM_BLOCK_RE.finditer(source):
        name = em.group("name")
        body = em.group("body")
        result["enums"][name] = _parse_enum_block(body)

    # Models
    for mm in _MODEL_RE.finditer(source):
        mname = mm.group("name")
        body = mm.group("body")
        model_info = _parse_model_body(body)
        # infer relations
        for f in model_info["fields"].values():
            if f["type"] in ("ForeignKey", "OneToOne", "ManyToOne"):
                # first param should be target model name
                target = str((f["params"] or [None])[0])
                if target:
                    result["relations"].append({
                        "kind": "fk",
                        "from": mname,
                        "field": f["name"],
                        "to": target,
                        "on_delete": f["kwargs"].get("on_delete", "CASCADE"),
                    })
        result["models"][mname] = model_info

    return result
