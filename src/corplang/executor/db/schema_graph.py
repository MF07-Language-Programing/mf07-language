"""SchemaGraph and Migration planning (minimal viable implementation).

Builds a simple graph from parsed models and computes migration plans:
- Initial: for new databases (create_enum, create_model, add_fk)
- Incremental: for existing databases (detects changes, generates alter/add/drop)
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


def compute_incremental_plan(previous_graph: Dict[str, Any], new_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute migration plan by comparing previous and new schema.
    
    Detects:
    - New models/enums -> create
    - Deleted models/enums -> drop (marked for deletion)
    - Modified fields -> alter_column or drop+add
    - New fields -> add_column
    - Deleted fields -> drop_column
    - New relations -> add_fk
    
    Returns list of operations in proper order.
    """
    ops: List[Dict[str, Any]] = []
    
    prev_models = previous_graph.get("models", {})
    new_models = new_graph.get("models", {})
    prev_enums = previous_graph.get("enums", {})
    new_enums = new_graph.get("enums", {})
    prev_rels = {(r["from"], r["field"]): r for r in previous_graph.get("relations", [])}
    new_rels = {(r["from"], r["field"]): r for r in new_graph.get("relations", [])}
    
    # 1. Create new enums
    for enum_name in set(new_enums.keys()) - set(prev_enums.keys()):
        ops.append({"op": "create_enum", "name": enum_name, "values": new_enums[enum_name]})
    
    # 2. Alter existing enums (if changed)
    for enum_name in set(new_enums.keys()) & set(prev_enums.keys()):
        prev_vals = prev_enums[enum_name]
        new_vals = new_enums[enum_name]
        
        # Normalize: convert both to comparable format (tuples)
        prev_normalized = {tuple(v) if isinstance(v, (list, tuple)) else (v, v) for v in prev_vals}
        new_normalized = {tuple(v) if isinstance(v, (list, tuple)) else (v, v) for v in new_vals}
        
        if prev_normalized != new_normalized:
            ops.append({"op": "alter_enum", "name": enum_name, "values": new_enums[enum_name]})
    
    # 3. Create new models
    for model_name in set(new_models.keys()) - set(prev_models.keys()):
        info = new_models[model_name]
        table = info.get("table") or model_name.lower()
        fields = list(info.get("fields", {}).values())
        ops.append({"op": "create_model", "model": model_name, "table": table, "fields": fields})
    
    # 4. Alter existing models (fields)
    for model_name in set(new_models.keys()) & set(prev_models.keys()):
        prev_model_info = prev_models[model_name]
        new_model_info = new_models[model_name]
        
        # Handle field format: can be dict (with field data) or list (names only in snapshot)
        prev_fields_raw = prev_model_info.get("fields", {})
        new_fields_raw = new_model_info.get("fields", {})
        
        # Normalize: if list, convert to set of names; if dict, use keys
        if isinstance(prev_fields_raw, list):
            prev_field_names = set(prev_fields_raw)
            prev_fields = {name: {"type": "Unknown"} for name in prev_field_names}
        else:
            prev_fields = prev_fields_raw
        
        if isinstance(new_fields_raw, list):
            new_field_names = set(new_fields_raw)
            new_fields = {name: {"type": "Unknown"} for name in new_field_names}
        else:
            new_fields = new_fields_raw
        
        table = new_model_info.get("table") or model_name.lower()
        
        # New fields
        for field_name in set(new_fields.keys()) - set(prev_fields.keys()):
            field_data = new_fields[field_name]
            ops.append({
                "op": "add_column",
                "model": model_name,
                "table": table,
                "field_name": field_name,
                "field_def": field_data,
            })
        
        # Deleted fields
        for field_name in set(prev_fields.keys()) - set(new_fields.keys()):
            ops.append({
                "op": "drop_column",
                "model": model_name,
                "table": table,
                "field_name": field_name,
            })
        
        # Modified fields (in common) - skip if old_def is placeholder
        for field_name in set(prev_fields.keys()) & set(new_fields.keys()):
            prev_def = prev_fields[field_name]
            new_def = new_fields[field_name]
            
            # Skip comparison if previous was unknown type (from snapshot list)
            if prev_def.get("type") == "Unknown":
                continue
            
            if prev_def != new_def:
                ops.append({
                    "op": "alter_column",
                    "model": model_name,
                    "table": table,
                    "field_name": field_name,
                    "old_def": prev_def,
                    "new_def": new_def,
                })
    
    # 5. Drop deleted models
    for model_name in set(prev_models.keys()) - set(new_models.keys()):
        table = prev_models[model_name].get("table") or model_name.lower()
        ops.append({"op": "drop_model", "model": model_name, "table": table})
    
    # 6. Add new foreign keys
    for (from_m, field) in set(new_rels.keys()) - set(prev_rels.keys()):
        ops.append({"op": "add_fk", **new_rels[(from_m, field)]})
    
    # 7. Drop deleted foreign keys
    for (from_m, field) in set(prev_rels.keys()) - set(new_rels.keys()):
        ops.append({"op": "drop_fk", **prev_rels[(from_m, field)]})
    
    return ops
