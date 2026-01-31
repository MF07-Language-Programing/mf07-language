"""PostgreSQL migration driver."""
from typing import Any, Dict, List
from .base import MigrationDriver


class PostgreSQLDriver(MigrationDriver):
    """PostgreSQL-specific migration implementation."""
    
    @staticmethod
    def get_field_type(field_def: Dict[str, Any]) -> str:
        """Convert field to PostgreSQL type."""
        t = field_def.get("type")
        params = field_def.get("params", [])
        kwargs = field_def.get("kwargs", {})

        if t == "AutoField":
            return "SERIAL PRIMARY KEY"
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
            return "TIMESTAMP WITH TIME ZONE"
        if t == "DateField":
            return "DATE"
        if t == "EnumField":
            enum_name = field_def.get("enum_name")
            if enum_name:
                return enum_name.lower()
            return "TEXT"
        
        return "TEXT"
    
    @staticmethod
    def apply_operations(conn: Any, operations: List[Dict[str, Any]], graph: Dict[str, Any]) -> None:
        """Apply migration operations to PostgreSQL database."""
        cur = conn.cursor()
        
        try:
            # Process operations
            for op in operations:
                op_type = op.get("op") or op.get("type")
                
                if op_type == "create_enum":
                    _create_enum_postgres(cur, op)
                elif op_type == "create_model":
                    _create_table_postgres(cur, op, graph)
                elif op_type == "add_column":
                    _add_column_postgres(cur, op, graph)
                elif op_type == "drop_column":
                    _drop_column_postgres(cur, op)
                elif op_type == "alter_column":
                    _alter_column_postgres(cur, op)
                elif op_type == "drop_model":
                    _drop_table_postgres(cur, op)
                elif op_type == "alter_enum":
                    _alter_enum_postgres(cur, op)
                elif op_type == "add_fk":
                    _add_fk_postgres(cur, op, graph)
                elif op_type == "drop_fk":
                    _drop_fk_postgres(cur, op)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"PostgreSQL migration failed: {e}") from e


def _create_enum_postgres(cur: Any, op: Dict[str, Any]) -> None:
    """Create enum type in PostgreSQL."""
    enum_name = op["name"].lower()
    values = op.get("values", [])
    
    vals_str = ", ".join(f"'{v[0]}'" if isinstance(v, (list, tuple)) else f"'{v}'" for v in values)
    ddl = f"CREATE TYPE {enum_name} AS ENUM ({vals_str})"
    
    cur.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE")
    cur.execute(ddl)


def _create_table_postgres(cur: Any, op: Dict[str, Any], graph: Dict[str, Any]) -> None:
    """Create table in PostgreSQL with proper type mapping."""
    table = op["table"]
    fields = op.get("fields", [])
    
    if not fields:
        return
    
    # Build column definitions
    cols = []
    
    for field_def in fields:
        name = field_def.get("name")
        field_type = PostgreSQLDriver.get_field_type(field_def)
        
        # Quote column names to avoid reserved word conflicts
        col = f'  "{name}" {field_type}'
        
        kwargs = field_def.get("kwargs", {})

        # NOT NULL
        if not kwargs.get("null"):
            col += " NOT NULL"
        
        # DEFAULT (auto_now/auto_now_add take precedence)
        auto_now = kwargs.get("auto_now") or kwargs.get("auto_now_add")
        default = kwargs.get("default")
        if auto_now:
            col += " DEFAULT CURRENT_TIMESTAMP"
        elif default is not None:
            col += f" DEFAULT {MigrationDriver._sql_value(default)}"
        
        # UNIQUE
        if kwargs.get("unique"):
            col += " UNIQUE"
        
        cols.append(col)
    
    # Note: Foreign keys are added via separate add_fk operations
    # to ensure proper dependency ordering between tables
    
    ddl = f"CREATE TABLE IF NOT EXISTS \"{table}\" (\n"
    ddl += ",\n".join(cols)
    ddl += "\n)"
    
    cur.execute(ddl)


def _add_column_postgres(cur: Any, op: Dict[str, Any], graph: Dict[str, Any]) -> None:
    """Add column to existing table."""
    table = op["table"]
    field_name = op["field_name"]
    field_def = op["field_def"]
    
    field_type = PostgreSQLDriver.get_field_type(field_def)
    
    ddl = f'ALTER TABLE {table} ADD COLUMN "{field_name}" {field_type}'

    kwargs = field_def.get("kwargs", {})
    auto_now = kwargs.get("auto_now") or kwargs.get("auto_now_add")
    default = kwargs.get("default")

    if auto_now:
        ddl += " DEFAULT CURRENT_TIMESTAMP"
    elif default is not None:
        ddl += f" DEFAULT {MigrationDriver._sql_value(default)}"

    if not kwargs.get("null"):
        ddl += " NOT NULL"
    
    cur.execute(ddl)


def _drop_column_postgres(cur: Any, op: Dict[str, Any]) -> None:
    """Drop column from table."""
    table = op["table"]
    field_name = op["field_name"]
    cur.execute(f'ALTER TABLE {table} DROP COLUMN IF EXISTS "{field_name}" CASCADE')


def _alter_column_postgres(cur: Any, op: Dict[str, Any]) -> None:
    """Alter column type/constraints."""
    table = op["table"]
    field_name = op["field_name"]
    new_def = op.get("new_def", {})
    
    new_type = PostgreSQLDriver.get_field_type(new_def)
    
    # Change type
    cur.execute(f'ALTER TABLE {table} ALTER COLUMN "{field_name}" TYPE {new_type}')
    
    # NOT NULL
    nullable = new_def.get("kwargs", {}).get("null")
    if nullable is False:
        cur.execute(f'ALTER TABLE {table} ALTER COLUMN "{field_name}" SET NOT NULL')
    elif nullable is True:
        cur.execute(f'ALTER TABLE {table} ALTER COLUMN "{field_name}" DROP NOT NULL')
    
    # DEFAULT
    kwargs = new_def.get("kwargs", {})
    auto_now = kwargs.get("auto_now") or kwargs.get("auto_now_add")
    default = kwargs.get("default")
    if auto_now:
        cur.execute(f'ALTER TABLE {table} ALTER COLUMN "{field_name}" SET DEFAULT CURRENT_TIMESTAMP')
    elif default is not None:
        cur.execute(f'ALTER TABLE {table} ALTER COLUMN "{field_name}" SET DEFAULT {MigrationDriver._sql_value(default)}')
    else:
        cur.execute(f'ALTER TABLE {table} ALTER COLUMN "{field_name}" DROP DEFAULT')


def _drop_table_postgres(cur: Any, op: Dict[str, Any]) -> None:
    """Drop table."""
    table = op["table"]
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")


def _alter_enum_postgres(cur: Any, op: Dict[str, Any]) -> None:
    """Alter enum type by dropping and recreating."""
    enum_name = op["name"].lower()
    values = op.get("values", [])
    
    cur.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE")
    
    vals_str = ", ".join(f"'{v[0]}'" if isinstance(v, (list, tuple)) else f"'{v}'" for v in values)
    ddl = f"CREATE TYPE {enum_name} AS ENUM ({vals_str})"
    cur.execute(ddl)


def _add_fk_postgres(cur: Any, op: Dict[str, Any], graph: Dict[str, Any]) -> None:
    """Add foreign key constraint to existing table."""
    from_model = op.get("from", "")
    from_table = graph.get("models", {}).get(from_model, {}).get("table", from_model.lower())
    from_field = op.get("field", "")
    to_model = op.get("to", "")
    to_table = graph.get("models", {}).get(to_model, {}).get("table", to_model.lower())
    fk_name = f"fk_{from_table}_{from_field}"
    
    cur.execute(f'ALTER TABLE "{from_table}" ADD CONSTRAINT {fk_name} FOREIGN KEY ("{from_field}") REFERENCES "{to_table}" (id)')


def _drop_fk_postgres(cur: Any, op: Dict[str, Any]) -> None:
    """Drop foreign key constraint."""
    from_table = op.get("from", "").lower()
    from_field = op.get("field", "")
    fk_name = f"fk_{from_table}_{from_field}"
    
    cur.execute(f"ALTER TABLE {from_table} DROP CONSTRAINT IF EXISTS {fk_name} CASCADE")
