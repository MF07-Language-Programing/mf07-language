"""SchemaGraph and Migration planning (minimal viable implementation).

Builds a simple graph from parsed models and computes a migration plan
for initial creation (create_enum, create_model, add_field, add_fk).
"""
from __future__ import annotations
from typing import Any, Dict, List


def build_graph(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Return a canonical-ish graph representation (minimal)."""
    return {
        "enums": schema.get("enums", {}),
        "models": schema.get("models", {}),
        "relations": schema.get("relations", []),
    }


def compute_initial_plan(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute a straightforward initial plan.
    Order: create_enum -> create_model -> add_field (non-pk) -> add_fk
    For simplicity, fields are applied during create_model; FKs added after.
    """
    ops: List[Dict[str, Any]] = []

    # enums first
    for en_name, items in graph.get("enums", {}).items():
        ops.append({"op": "create_enum", "name": en_name, "values": items})

    # models
    for mname, info in graph.get("models", {}).items():
        table = info.get("table") or mname.lower()
        fields = list(info.get("fields", {}).values())
        ops.append({"op": "create_model", "model": mname, "table": table, "fields": fields})

    # add_fk
    for rel in graph.get("relations", []):
        if rel.get("kind") == "fk":
            ops.append({"op": "add_fk", **rel})

    return ops
