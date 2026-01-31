"""Migration execution engine supporting multiple databases.

Writes migration snapshots and plans. Applies migrations via driver-specific adapters.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List


def _table_name_from_graph(graph: Dict[str, Any], model_name: str) -> str:
    models = graph.get("models", {})
    model_def = models.get(model_name, {}) if isinstance(models, dict) else {}
    return model_def.get("table") or model_name.lower()


def drop_schema(driver: str, dsn: str, graph: Dict[str, Any]) -> None:
    """Drop all tables/enums present in the snapshot graph for the given driver."""
    tables: List[str] = []
    enums: List[str] = []

    if graph:
        enums = list(graph.get("enums", {}).keys()) if isinstance(graph.get("enums"), dict) else []
        models = graph.get("models", {})
        if isinstance(models, dict):
            tables = [_table_name_from_graph(graph, name) for name in models.keys()]

    driver_l = driver.lower()

    if driver_l in ("sqlite",):
        import sqlite3
        conn = sqlite3.connect(dsn)
        try:
            cur = conn.cursor()
            for table in tables:
                cur.execute(f'DROP TABLE IF EXISTS "{table}"')
            conn.commit()
        finally:
            conn.close()
        return

    if driver_l in ("postgresql", "postgres"):
        try:
            import psycopg
            conn = psycopg.connect(dsn)
        except ImportError:
            import psycopg2
            conn = psycopg2.connect(dsn)

        try:
            cur = conn.cursor()
            for table in tables:
                cur.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
            for enum in enums:
                cur.execute(f"DROP TYPE IF EXISTS {enum.lower()} CASCADE")
            conn.commit()
        finally:
            conn.close()
        return

    raise ValueError(f"Unsupported driver for drop_schema: {driver}")


def _generate_migration_name(ops: List[Dict[str, Any]]) -> str:
    """Generate short descriptive name for migration based on operations."""
    if not ops:
        return "empty"
    
    names = []
    for op in ops[:3]:
        op_type = op.get("op") or op.get("type", "")
        if op_type == "create_model":
            model = op.get("model", "")
            names.append(f"create_{model.lower()}")
        elif op_type == "add_column":
            field = op.get("field_name", "")
            names.append(f"add_{field}")
        elif op_type == "drop_column":
            field = op.get("field_name", "")
            names.append(f"drop_{field}")
        elif op_type == "alter_column":
            field = op.get("field_name", "")
            names.append(f"alter_{field}")
        elif op_type == "create_enum":
            enum = op.get("name", "")
            names.append(f"enum_{enum.lower()}")
        elif op_type == "add_fk":
            field = op.get("field", "")
            names.append(f"fk_{field}")
        elif op_type == "drop_model":
            model = op.get("model", "")
            names.append(f"drop_{model.lower()}")
    
    return "_".join(names[:2]) if names else "migration"


def get_next_migration_number(mig_dir: Path) -> int:
    """Get next migration sequence number."""
    existing = [f.stem for f in mig_dir.glob("*.json") if f.stem[0].isdigit()]
    if not existing:
        return 1
    numbers = [int(f.split("_")[0]) for f in existing if "_" in f]
    return max(numbers, default=0) + 1 if numbers else 1


def get_applied_migrations(mig_dir: Path) -> set:
    """Get set of already-applied migration filenames."""
    applied_file = mig_dir / ".applied"
    if not applied_file.exists():
        return set()
    try:
        data = json.loads(applied_file.read_text())
        return set(data.get("applied", []))
    except:
        return set()


def mark_migration_applied(mig_dir: Path, filename: str) -> None:
    """Mark a migration as applied."""
    applied_file = mig_dir / ".applied"
    applied = get_applied_migrations(mig_dir)
    applied.add(filename)
    applied_file.write_text(json.dumps({"applied": sorted(applied)}, ensure_ascii=False, indent=2))


def write_snapshot(snapshot_path: Path, graph: Dict[str, Any]) -> None:
    """Write current schema snapshot for incremental migration detection."""
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "enums": graph.get("enums", {}),
        "models": graph.get("models", {}),
        "relations": graph.get("relations", []),
    }
    snapshot_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))


def write_migration(mig_dir: Path, ops: List[Dict[str, Any]]) -> Path:
    """Write a single migration file with sequential naming and descriptive suffix.
    
    Returns path to the created migration file.
    """
    mig_dir.mkdir(parents=True, exist_ok=True)
    
    num = get_next_migration_number(mig_dir)
    name = _generate_migration_name(ops)
    filename = f"{num:03d}_{name}.json"
    path = mig_dir / filename
    
    path.write_text(json.dumps({"ops": ops}, ensure_ascii=False, indent=2))
    return path


def apply_migrations(driver: str, dsn: str, mig_dir: Path = None, graph: Dict[str, Any] = None) -> List[str]:
    """Apply all unapplied migrations in sequence.
    
    If mig_dir is provided, loads migrations from directory and tracks applied.
    Otherwise, applies single ops list (legacy behavior).
    
    Returns list of applied migration filenames.
    """
    from src.corplang.executor.db.drivers.registry import get_driver
    
    driver_class = get_driver(driver)
    applied_list = []
    
    if mig_dir is None:
        return applied_list
    
    if not mig_dir.exists():
        return applied_list
    
    mig_dir.mkdir(parents=True, exist_ok=True)
    
    migration_files = sorted([f for f in mig_dir.glob("*.json") if f.stem[0].isdigit()])
    applied = get_applied_migrations(mig_dir)
    
    if driver.lower() in ("sqlite",):
        import sqlite3
        conn = sqlite3.connect(dsn)
    elif driver.lower() in ("postgresql", "postgres"):
        try:
            import psycopg
            conn = psycopg.connect(dsn)
        except ImportError:
            import psycopg2
            conn = psycopg2.connect(dsn)
    else:
        raise ValueError(f"Unsupported driver: {driver}")
    
    try:
        for mig_file in migration_files:
            if mig_file.name in applied:
                continue
            
            plan_data = json.loads(mig_file.read_text())
            ops = plan_data.get("ops", [])
            
            driver_class.apply_operations(conn, ops, graph)
            mark_migration_applied(mig_dir, mig_file.name)
            applied_list.append(mig_file.name)
    finally:
        conn.close()
    
    return applied_list
