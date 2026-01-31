# Multi-Driver Migration System

Corplang's migration system now supports multiple database engines through a pluggable driver architecture.

## Supported Drivers

### SQLite
- **Driver name**: `sqlite`
- **DSN format**: `sqlite:///path/to/database.db` or `./database.db`
- **Use case**: Development, testing, small-scale apps
- **Features**:
  - ✅ CREATE TABLE
  - ✅ ADD COLUMN
  - ✅ DROP TABLE
  - ⚠️ ALTER/DROP COLUMN (requires table rebuild - TODO)

**Example config**:
```yaml
database:
  driver: "sqlite"
  dsn: "./app.db"
```

### PostgreSQL
- **Driver names**: `postgresql` or `postgres`
- **DSN format**: `postgresql://user:password@host:port/database`
- **Use case**: Production, high-performance, complex schemas
- **Features**:
  - ✅ CREATE TABLE
  - ✅ ADD COLUMN
  - ✅ ALTER COLUMN (with type changes, NOT NULL, DEFAULT)
  - ✅ DROP COLUMN
  - ✅ DROP TABLE
  - ✅ CREATE ENUM (native PostgreSQL types)
  - ✅ ALTER ENUM
  - ✅ Foreign Key constraints (with CASCADE)

**Example config**:
```yaml
database:
  driver: "postgresql"
  dsn: "postgresql://user:password@localhost:5432/myapp"
```

## Architecture

The migration system uses a **driver adapter pattern**:

```
User Code
    ↓
migrations.py (apply_migrations)
    ↓
drivers/registry.py (get_driver)
    ↓
Driver Class (SQLiteDriver, PostgreSQLDriver, etc.)
    ├── get_field_type()    → SQL type for field
    └── apply_operations()  → Execute DDL statements
```

### Adding a New Driver

1. Create `src/corplang/executor/db/drivers/your_driver.py`:

```python
from typing import Any, Dict, List
from .base import MigrationDriver

class YourDriver(MigrationDriver):
    @staticmethod
    def get_field_type(field_def: Dict[str, Any]) -> str:
        """Convert field to your database's SQL type."""
        t = field_def.get("type")
        if t == "CharField":
            return "VARCHAR(255)"
        # ... implement mappings
        return "TEXT"
    
    @staticmethod
    def apply_operations(conn: Any, operations: List[Dict[str, Any]], graph: Dict[str, Any]) -> None:
        """Apply migrations to your database."""
        cur = conn.cursor()
        try:
            for op in operations:
                # Implement operation handlers
                pass
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Migration failed: {e}") from e
```

2. Register in `src/corplang/executor/db/drivers/registry.py`:

```python
from .your_driver import YourDriver

DRIVERS: Dict[str, Type[MigrationDriver]] = {
    "sqlite": SQLiteDriver,
    "postgresql": PostgreSQLDriver,
    "your_database": YourDriver,  # Add here
}
```

3. Test with configuration:

```yaml
database:
  driver: "your_database"
  dsn: "your://connection/string"
```

## Field Type Mapping

Each driver maps Corplang field types to native SQL types:

| Corplang | SQLite | PostgreSQL |
|----------|--------|-----------|
| AutoField | INTEGER PRIMARY KEY AUTOINCREMENT | SERIAL PRIMARY KEY |
| CharField | VARCHAR(n) | VARCHAR(n) |
| TextField | TEXT | TEXT |
| IntegerField | INTEGER | INTEGER |
| DecimalField | NUMERIC(p,s) | NUMERIC(p,s) |
| BooleanField | BOOLEAN | BOOLEAN |
| DateTimeField | TEXT | TIMESTAMP WITH TIME ZONE |
| DateField | TEXT | DATE |
| ForeignKey | INTEGER | INTEGER |
| EnumField | TEXT | (native ENUM type) |

## Operation Support Matrix

| Operation | SQLite | PostgreSQL |
|-----------|--------|-----------|
| create_model | ✅ | ✅ |
| add_column | ✅ | ✅ |
| alter_column | ⚠️ TODO | ✅ |
| drop_column | ⚠️ TODO | ✅ |
| drop_model | ✅ | ✅ |
| create_enum | (via CHECK) | ✅ |
| alter_enum | (via CHECK) | ✅ |
| add_fk | (at create) | ✅ |
| drop_fk | ⚠️ TODO | ✅ |

## Usage

### Create Initial Migration
```bash
mf db makemigrations
# Creates migrations/plan.initial.json and migrations/schema.json
```

### Apply Migration
```bash
mf db migrate
# Applies plan.initial.json or plan.incremental.json (if present)
```

### Detect Field Changes
```bash
# Modify models.mp (add/remove/change fields)
mf db makemigrations
# Creates migrations/plan.incremental.json with detected changes
mf db migrate
# Applies incremental changes to database
```

## Best Practices

1. **Always test migrations** on a copy of production data
2. **Use PostgreSQL** for production environments
3. **Keep models.mp** in version control with migrations
4. **Run migrations** before deploying code changes
5. **Check migration plans** before running `migrate`:
   ```bash
   cat migrations/plan.initial.json  # Review changes
   mf db migrate                      # Apply when satisfied
   ```

## Limitations

### SQLite
- ALTER/DROP COLUMN requires full table rebuild (not implemented yet)
- No native ENUM type (uses CHECK constraints)
- Foreign key constraints must be enabled with PRAGMA

### PostgreSQL
- Enum types must be created before use
- Altering enums requires dropping dependent columns first
- Some schema changes may require explicit locks

## Troubleshooting

**"Unsupported driver" error**
- Check `language_config.yaml` driver name
- Ensure driver is registered in `drivers/registry.py`

**PostgreSQL connection fails**
- Verify DSN format: `postgresql://user:password@host:port/db`
- Check database server is running
- Verify credentials and network access

**"No migration plan found"**
- Run `mf db makemigrations` first
- Check `migrations/` directory exists
- Look for `plan.initial.json` or `plan.incremental.json`

**Field type mismatch**
- Check `get_field_type()` implementation in your driver
- Verify field parameters are passed correctly
- Look at generated DDL statements for clues
