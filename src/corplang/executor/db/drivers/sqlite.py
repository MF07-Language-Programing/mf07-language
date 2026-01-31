"""SQLite migration driver."""
from typing import Any, Dict, List
from .base import MigrationDriver


class SQLiteDriver(MigrationDriver):
    """SQLite-specific migration implementation."""
    
    @staticmethod
    def get_field_type(field_def: Dict[str, Any]) -> str:
        """Convert field to SQLite type."""
        t = field_def.get("type")
        params = field_def.get("params", [])
        kwargs = field_def.get("kwargs", {})

        if t == "AutoField":
            return "INTEGER PRIMARY KEY AUTOINCREMENT"
        if t == "ForeignKey":
            return "INTEGER"
        if t == "CharField":
            max_len = kwargs.get("max_length", 255)
            return f"VARCHAR({max_len})"
        if t == "TextField":
            return "TEXT"
        if t == "IntegerField":
            return "INTEGER"
        if t == "DecimalField":
            if params:
                return f"NUMERIC({params[0]},{params[1]})"
            return "NUMERIC"
        if t == "BooleanField":
            return "BOOLEAN"
        if t == "DateTimeField":
            return "TEXT"
        if t == "DateField":
            return "TEXT"
        if t == "EnumField":
            return "TEXT"
        
        return "TEXT"
    
    @staticmethod
    def apply_operations(conn: Any, operations: List[Dict[str, Any]], graph: Dict[str, Any]) -> None:
        """Apply migration operations to SQLite database."""
        cur = conn.cursor()
        
        try:
            # Enable foreign keys (disabled by default in SQLite)
            cur.execute("PRAGMA foreign_keys = ON")
            
            for op in operations:
                op_type = op.get("op") or op.get("type")
                
                if op_type == "create_model":
                    _create_table_sqlite(cur, op, graph)
                elif op_type == "add_column":
                    _add_column_sqlite(cur, op)
                elif op_type == "drop_column":
                    # SQLite limitation: requires table rebuild
                    pass
                elif op_type == "alter_column":
                    # SQLite limitation: requires table rebuild
                    pass
                elif op_type == "drop_model":
                    _drop_table_sqlite(cur, op)
                elif op_type == "create_enum":
                    # SQLite: enums handled via CHECK constraints in table
                    pass
                elif op_type == "alter_enum":
                    # SQLite: enum modification via table rebuild
                    pass
                elif op_type == "add_fk":
                    # SQLite: FK added at table creation, not separately
                    pass
                elif op_type == "drop_fk":
                    # SQLite: FK dropped via table rebuild
                    pass
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"SQLite migration failed: {e}") from e


def _create_table_sqlite(cur: Any, op: Dict[str, Any], graph: Dict[str, Any]) -> None:
    """Create table with fields and constraints."""
    table = op["table"]
    fields = op.get("fields", [])
    
    if not fields:
        return
    
    # Build column definitions
    cols = []
    constraints = []
    
    for field_def in fields:
        name = field_def.get("name")
        field_type = SQLiteDriver.get_field_type(field_def)
        
        col = f"  {name} {field_type}"
        
        # NOT NULL
        if not field_def.get("kwargs", {}).get("null"):
            col += " NOT NULL"
        
        # DEFAULT
        default = field_def.get("kwargs", {}).get("default")
        if default is not None:
            col += f" DEFAULT {MigrationDriver._sql_value(default)}"
        
        # UNIQUE
        if field_def.get("kwargs", {}).get("unique"):
            col += " UNIQUE"
        
        cols.append(col)
    
    # Build CHECK constraints for enums
    for field_def in fields:
        if field_def.get("type") == "EnumField":
            enum_name = None
            if field_def.get("params"):
                enum_name = field_def["params"][0]
            enum_vals = graph.get("enums", {}).get(enum_name, [])
            if enum_vals:
                vals_str = ", ".join(f"'{v[0]}'" if isinstance(v, (list, tuple)) else f"'{v}'" for v in enum_vals)
                constraints.append(f"  CHECK ({field_def['name']} IN ({vals_str}))")
    
    # Build FK constraints (note: user field is ForeignKey type)
    for field_def in fields:
        if field_def.get("type") == "ForeignKey":
            # ForeignKey params[0] contains the target model name
            to_model = None
            if field_def.get("params"):
                to_model = field_def["params"][0]
            if to_model:
                table_name = to_model.lower()
                constraints.append(f"  FOREIGN KEY ({field_def['name']}) REFERENCES {table_name} (id)")
    
    ddl = f"CREATE TABLE IF NOT EXISTS {table} (\n"
    ddl += ",\n".join(cols)
    if constraints:
        ddl += ",\n" + ",\n".join(constraints)
    ddl += "\n)"
    
    cur.execute(ddl)


def _add_column_sqlite(cur: Any, op: Dict[str, Any]) -> None:
    """Add column to existing table (SQLite supports simple ADD)."""
    table = op["table"]
    field_name = op["field_name"]
    field_def = op["field_def"]
    
    field_type = SQLiteDriver.get_field_type(field_def)
    
    ddl = f"ALTER TABLE {table} ADD COLUMN {field_name} {field_type}"
    
    # NOT NULL with default
    if not field_def.get("kwargs", {}).get("null"):
        default = field_def.get("kwargs", {}).get("default")
        if default is not None:
            ddl += f" DEFAULT {MigrationDriver._sql_value(default)}"
    
    cur.execute(ddl)


def _drop_table_sqlite(cur: Any, op: Dict[str, Any]) -> None:
    """Drop table."""
    table = op["table"]
    cur.execute(f"DROP TABLE IF EXISTS {table}")
