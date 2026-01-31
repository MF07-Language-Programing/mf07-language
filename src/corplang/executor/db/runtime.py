"""Runtime DB connector and ORM bridge for .mp code.

Exposes:
- db.connect(url) -> opens connection
- Model.create(**kwargs) -> INSERT
- Model.objects.all() -> SELECT * list of dicts
- Model.objects.filter(field=value) -> SELECT WHERE

Minimal viable implementation: SQLite/PostgreSQL, direct SQL, no caching.
"""
from __future__ import annotations
import re
import sqlite3
from typing import Any, Dict, List, Optional
from pathlib import Path


def serialize_value_for_db(value: Any) -> Any:
    """Convert Python/enum values to database-compatible format."""
    from src.corplang.runtime.enums import EnumValue
    if isinstance(value, EnumValue):
        return value.value
    return value


def deserialize_value_from_db(value: Any, field_def: Dict[str, Any], model_fields: Dict[str, Any]) -> Any:
    """Convert database values back to Python/enum objects."""
    if value is None:
        return None
    
    field_type = field_def.get("type")
    if field_type == "EnumField":
        # Try to get enum class from params (first positional arg)
        params = field_def.get("params", [])
        if params:
            enum_name = params[0]
            # Look up enum in ModelRegistry enums
            enum_obj = ModelRegistry.get_enum(enum_name)
            if enum_obj:
                # Find matching enum member by value
                for attr_name in dir(enum_obj):
                    if not attr_name.startswith('_'):
                        member = getattr(enum_obj, attr_name, None)
                        from src.corplang.runtime.enums import EnumValue
                        if isinstance(member, EnumValue) and member.value == value:
                            return member
        return value
    
    return value


class DBConnection:
    def __init__(self):
        self.conn: Any = None
        self.driver: str = ""
        self.backend: str = ""  # sqlite | psycopg3 | psycopg2
        self.dsn: str = ""

    def connect(self, url: str):
        """Parse DB URL and open connection."""
        if url.startswith("sqlite://"):
            self._connect_sqlite(url)
        elif url.startswith(("postgresql://", "postgres://")):
            self._connect_postgres(url)
        else:
            raise ValueError(f"Unsupported DB URL: {url}")

    # ---------- Backends ----------

    def _connect_sqlite(self, url: str):
        self.driver = "sqlite"
        self.backend = "sqlite"
        self.dsn = url[len("sqlite://"):]
        self.conn = sqlite3.connect(self.dsn)
        self.conn.row_factory = sqlite3.Row

    def _connect_postgres(self, url: str):
        self.driver = "postgresql"
        self.dsn = url

        # Prefer psycopg v3
        try:
            import psycopg
            self.conn = psycopg.connect(url)
            self.backend = "psycopg3"
            return
        except ImportError:
            pass

        # Fallback psycopg2
        try:
            import psycopg2
            self.conn = psycopg2.connect(url)
            self.backend = "psycopg2"
            return
        except ImportError:
            raise RuntimeError(
                "PostgreSQL driver missing. Install one of:\n"
                "  - psycopg[binary] (recommended)\n"
                "  - psycopg2-binary (legacy fallback)"
            )

    # ---------- Query API ----------

    def execute(self, sql: str, params: Optional[tuple] = None) -> Any:
        if not self.conn:
            raise RuntimeError("Not connected to DB")

        cur = self.conn.cursor()
        cur.execute(sql, params or ())
        return cur

    def fetchall(
            self, sql: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        cur = self.execute(sql, params)
        rows = cur.fetchall()
        if not rows:
            return []

        if self.backend == "sqlite":
            return [dict(r) for r in rows]

        # psycopg2 / psycopg3
        cols = [d.name if hasattr(d, "name") else d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in rows]

    # ---------- Transaction control ----------

    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.backend = ""


_connection = DBConnection()


def connect(url: str):
    """Open DB connection from .mp code: db.connect("sqlite://app.db")"""
    _connection.connect(url)


def auto_connect_from_config():
    """Auto-connect to database from language_config.yaml if configured.
    
    This is called when 'import db' is executed.
    Only connects if config exists and connection not already established.
    """
    global _connection
    
    # Only auto-connect once
    if _connection.conn is not None:
        return
    
    try:
        from src.commands.config import CorplangConfig
        
        project_root = CorplangConfig.get_project_root()
        if not project_root:
            return
        
        driver, dsn = CorplangConfig.load_database_config(project_root)
        
        # Build URL
        if driver == "sqlite":
            url = f"sqlite://{dsn}"
        elif driver == "postgresql":
            url = dsn  # Assume full URL for postgresql
        else:
            return
        
        _connection.connect(url)
    except Exception:
        # Silently fail - user can call connect() explicitly if needed
        pass



def _get_connection() -> DBConnection:
    return _connection


class ModelRegistry:
    """Stores model metadata for runtime ORM."""
    _models: Dict[str, Dict[str, Any]] = {}
    _enums: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, table: str, fields: Dict[str, Any]):
        cls._models[name] = {"table": table, "fields": fields}

    @classmethod
    def get(cls, name: str) -> Optional[Dict[str, Any]]:
        return cls._models.get(name)
    
    @classmethod
    def register_enum(cls, name: str, enum_obj: Any):
        cls._enums[name] = enum_obj
    
    @classmethod
    def get_enum(cls, name: str) -> Optional[Any]:
        return cls._enums.get(name)


class BaseModel:
    """Base class for all models in .mp code.
    
    Acts as marker for model parsing/registration.
    Actual ORM methods (.create, .objects) come from ModelClass at runtime.
    """
    pass


class QuerySet:
    """Minimal QuerySet for .objects.all() / .filter() / .get() / .count()"""

    def __init__(self, model_name: str, table: str, fields: Dict[str, Any], driver: str = "sqlite"):
        self.model_name = model_name
        self.table = table
        self.fields = fields
        self._where: List[tuple] = []
        self.driver = driver

    def filter(self, **kwargs) -> QuerySet:
        qs = QuerySet(self.model_name, self.table, self.fields, self.driver)
        qs._where = self._where.copy()
        for k, v in kwargs.items():
            qs._where.append((k, v))
        return qs

    def all(self) -> List[Dict[str, Any]]:
        conn = _get_connection()
        sql = f"SELECT * FROM {self.table}"
        params = []
        if self._where:
            # Use correct placeholder for driver
            placeholder = "?" if self.driver == "sqlite" else "%s"
            # Serialize enum values in WHERE clause
            clauses = [f"{k} = {placeholder}" for k, _ in self._where]
            sql += " WHERE " + " AND ".join(clauses)
            params = [serialize_value_for_db(v) for _, v in self._where]
        rows = conn.fetchall(sql, tuple(params) if params else None)
        
        # Deserialize enum values from database
        deserialized = []
        for row in rows:
            new_row = {}
            for col, val in row.items():
                field_def = self.fields.get(col, {})
                new_row[col] = deserialize_value_from_db(val, field_def, self.fields)
            deserialized.append(new_row)
        
        return deserialized

    def get(self) -> Dict[str, Any]:
        """Fetch single row. Raise error if 0 or >1 rows match."""
        rows = self.all()
        if len(rows) == 0:
            raise RuntimeError(f"No {self.model_name} found matching filter")
        if len(rows) > 1:
            raise RuntimeError(f"Multiple {self.model_name} found, expected exactly 1")
        return rows[0]

    def exists(self) -> bool:
        """Check if any row matches filter."""
        return len(self.all()) > 0

    def count(self) -> int:
        """Count rows matching filter."""
        return len(self.all())

    def __iter__(self):
        return iter(self.all())


class ModelManager:
    """Model.objects manager."""

    def __init__(self, model_name: str):
        meta = ModelRegistry.get(model_name)
        if not meta:
            raise RuntimeError(f"Model {model_name} not registered")
        self.model_name = model_name
        self.table = meta["table"]
        self.fields = meta["fields"]

    def _get_driver(self) -> str:
        """Get current DB driver."""
        conn = _get_connection()
        return conn.driver or "sqlite"

    def all(self) -> List[Dict[str, Any]]:
        driver = self._get_driver()
        qs = QuerySet(self.model_name, self.table, self.fields, driver)
        return qs.all()

    def filter(self, **kwargs) -> QuerySet:
        driver = self._get_driver()
        qs = QuerySet(self.model_name, self.table, self.fields, driver)
        return qs.filter(**kwargs)

    def get(self, **kwargs) -> Dict[str, Any]:
        """Get single row matching filter. Error if 0 or >1."""
        driver = self._get_driver()
        qs = QuerySet(self.model_name, self.table, self.fields, driver)
        if kwargs:
            qs = qs.filter(**kwargs)
        return qs.get()

    def count(self) -> int:
        """Count all rows."""
        driver = self._get_driver()
        qs = QuerySet(self.model_name, self.table, self.fields, driver)
        return qs.count()

    def exists(self) -> bool:
        """Check if any row exists."""
        driver = self._get_driver()
        qs = QuerySet(self.model_name, self.table, self.fields, driver)
        return qs.exists()


class ModelClass:
    """Represents a Model class in runtime with .create and .objects."""

    def __init__(self, name: str):
        self.name = name
        meta = ModelRegistry.get(name)
        if not meta:
            raise RuntimeError(f"Model {name} not registered")
        self.table = meta["table"]
        self.fields = meta["fields"]
        self.objects = ModelManager(name)

    def create(self, **kwargs) -> Dict[str, Any]:
        """INSERT row and return inserted dict."""
        conn = _get_connection()
        cols = list(kwargs.keys())
        # Serialize enum values to strings
        vals = [serialize_value_for_db(v) for v in kwargs.values()]
        # Use correct placeholder for driver
        placeholder = "?" if conn.driver == "sqlite" else "%s"
        placeholders = ", ".join([placeholder for _ in vals])
        sql = f"INSERT INTO {self.table} ({', '.join(cols)}) VALUES ({placeholders})"
        cur = conn.execute(sql, tuple(vals))
        conn.commit()
        # Return inserted row (minimal: just echo kwargs + id if auto)
        row_id = cur.lastrowid if hasattr(cur, "lastrowid") else None
        result = dict(kwargs)
        if row_id:
            result["id"] = row_id
        return result


def load_models_from_file(models_file: Path):
    """Parse models.mp and register them in ModelRegistry. Returns dict of ModelClass instances."""
    from src.corplang.executor.db.model_parser import parse_models
    source = models_file.read_text(encoding="utf-8")
    schema = parse_models(source)
    result = {}
    for mname, info in schema.get("models", {}).items():
        table = info.get("table") or mname.lower()
        fields = info.get("fields", {})
        ModelRegistry.register(mname, table, fields)
        result[mname] = ModelClass(mname)
    return result


def get_model_class(name: str) -> ModelClass:
    """Return ModelClass for given name (used by interpreter to expose User, Order, etc.)"""
    return ModelClass(name)
