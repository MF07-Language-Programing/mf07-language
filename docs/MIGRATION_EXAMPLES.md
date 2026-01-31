# Multi-Driver Migrations - Examples

## Example 1: SQLite (Development)

### Configuration
```yaml
# language_config.yaml
database:
  driver: "sqlite"
  dsn: "./dev.db"
```

### Commands
```bash
# Create initial migration
mf db makemigrations

# Apply to database
mf db migrate

# Modify model (add field)
# Then:
mf db makemigrations  # Detects changes
mf db migrate         # Applies incremental changes
```

### Result
```
✓ Models Discovered
  └── Order model with 8 fields
ℹ Creating initial migration plan...
✓ Migrations generated: migrations/plan.initial.json

ℹ Using database: sqlite://./dev.db
✓ Applied migrations to sqlite://./dev.db
✓ migrate completed
```

## Example 2: PostgreSQL (Production)

### Configuration
```yaml
# language_config.yaml
database:
  driver: "postgresql"
  dsn: "postgresql://appuser:secret@prod.db.example.com:5432/myapp"
```

### Commands
```bash
# Same commands work automatically!
mf db makemigrations
mf db migrate
```

### PostgreSQL-Specific Features
```python
# ALTER COLUMN - fully supported
# Example: changing VARCHAR(255) → VARCHAR(500)
# PostgreSQL will:
# 1. ALTER TABLE users ALTER COLUMN name TYPE VARCHAR(500)

# DROP COLUMN - supported natively
# Example: removing unused fields
# PostgreSQL will:
# 1. ALTER TABLE users DROP COLUMN legacy_field CASCADE

# ENUM types - native support
# Corplang creates actual PostgreSQL ENUM types
# Example:
enum OrderStatus {
    PENDING,
    IN_PROGRESS,
    COMPLETED,
    CANCELED
}
# Creates:
# CREATE TYPE orderstatus AS ENUM ('PENDING', 'IN_PROGRESS', ...)
```

## Example 3: Multi-Driver Comparison

### Migration Operations Matrix

| Operation | SQLite | PostgreSQL | Result |
|-----------|--------|-----------|--------|
| CREATE TABLE | ✅ | ✅ | Works in both |
| ADD COLUMN | ✅ | ✅ | Works in both |
| ALTER COLUMN TYPE | ⏳ TODO | ✅ | PostgreSQL only |
| DROP COLUMN | ⏳ TODO | ✅ | PostgreSQL only |
| CREATE ENUM | ❌ (CHECK) | ✅ | Native in PostgreSQL |

### Why Choose Each?

**SQLite**: Development, Testing, Small Projects
```yaml
database:
  driver: "sqlite"
  dsn: "./test.db"  # File-based, no server needed
```
- ✅ Easy to set up
- ✅ No separate server
- ✅ Perfect for learning
- ⚠️ Limited concurrency
- ⚠️ Limited ALTER operations

**PostgreSQL**: Production, Complex Schemas
```yaml
database:
  driver: "postgresql"
  dsn: "postgresql://user:pass@host:5432/db"
```
- ✅ Full ALTER support
- ✅ Native ENUM types
- ✅ ACID compliance
- ✅ Handles concurrent migrations
- ✅ Excellent for teams

## Example 4: Incremental Migrations

### Initial State
```mp
model User extends Model {
    id = AutoField()
    email = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=true)
    table = "users"
}
```

```bash
mf db makemigrations
# Creates: migrations/plan.initial.json
mf db migrate
# Creates users table with 3 columns
```

### First Update
```mp
model User extends Model {
    id = AutoField()
    email = CharField(max_length=255)
    phone = CharField(max_length=20, null=true)  # NEW FIELD
    created_at = DateTimeField(auto_now_add=true)
    table = "users"
}
```

```bash
mf db makemigrations
# Creates: migrations/plan.incremental.json
# Detects: ADD COLUMN phone
mf db migrate
# ALTER TABLE users ADD COLUMN phone VARCHAR(20)
```

### Second Update
```mp
model User extends Model {
    id = AutoField()
    email = CharField(max_length=255)
    phone = CharField(max_length=20, null=true)
    username = CharField(max_length=100)  # NEW
    created_at = DateTimeField(auto_now_add=true)
    updated_at = DateTimeField(auto_now=true)  # NEW
    table = "users"
}
```

```bash
mf db makemigrations
# Creates: migrations/plan.incremental.json
# Detects:
#   - ADD COLUMN username
#   - ADD COLUMN updated_at
mf db migrate
# Executes both ADD COLUMN statements
```

## Example 5: Field Type Changes

### With PostgreSQL

```mp
# Before
model Product extends Model {
    id = AutoField()
    price = IntegerField()  # Price in cents
    table = "products"
}

# After
model Product extends Model {
    id = AutoField()
    price = DecimalField(10, 2)  # Price in dollars.cents
    table = "products"
}
```

```bash
mf db makemigrations
# Detects: ALTER COLUMN price
# Plan shows: IntegerField → DecimalField(10,2)

mf db migrate
# PostgreSQL executes:
# ALTER TABLE products ALTER COLUMN price TYPE NUMERIC(10,2)
```

### With SQLite

```bash
mf db makemigrations
# Detects: ALTER COLUMN price (marked as TODO)

mf db migrate
# SQLite marks as incomplete
# Requires manual table rebuild (future enhancement)
```

## Example 6: Enum Operations

### SQLite Handling
```mp
enum Status {
    ACTIVE,
    INACTIVE,
    PENDING
}
```

```bash
mf db makemigrations
# Plan includes: create_enum Status

mf db migrate
# SQLite creates CHECK constraint:
# CHECK (status IN ('ACTIVE', 'INACTIVE', 'PENDING'))
```

### PostgreSQL Handling
```bash
mf db makemigrations
# Plan includes: create_enum Status

mf db migrate
# PostgreSQL creates native ENUM type:
# CREATE TYPE status AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING')
# Column uses: status TYPE status
# More efficient and type-safe than CHECK
```

## Example 7: Complex Schema

```mp
enum OrderStatus { PENDING, SHIPPED, DELIVERED }
enum PaymentStatus { UNPAID, PAID, REFUNDED }

model Customer extends Model {
    id = AutoField()
    name = CharField(max_length=255)
    email = CharField(max_length=255, unique=true)
    phone = CharField(max_length=20, null=true)
    created_at = DateTimeField(auto_now_add=true)
    table = "customers"
}

model Order extends Model {
    id = AutoField()
    customer = ForeignKey(Customer)
    status = EnumField(OrderStatus, default=OrderStatus.PENDING)
    total = DecimalField(12, 2)
    created_at = DateTimeField(auto_now_add=true)
    table = "orders"
}

model Payment extends Model {
    id = AutoField()
    order = ForeignKey(Order)
    status = EnumField(PaymentStatus, default=PaymentStatus.UNPAID)
    amount = DecimalField(12, 2)
    processed_at = DateTimeField(null=true)
    table = "payments"
}
```

```bash
# First time
mf db makemigrations
# Generates complete schema with:
# - 2 enum types
# - 3 tables
# - Foreign keys
# - Constraints

mf db migrate
# Creates all tables in correct order (enums first, then tables with FKs)
```

## Best Practices

### Development Flow
```bash
# 1. Edit models.mp
vim models.mp

# 2. Generate migration (review changes)
mf db makemigrations

# 3. Check what will be applied
cat migrations/plan.incremental.json

# 4. Apply to database
mf db migrate

# 5. Test your app
mf run main.mp
```

### Production Workflow
```bash
# 1. On development machine
mf db makemigrations
git add migrations/plan.*.json migrations/schema.json
git commit -m "migrations: add user phone field"
git push

# 2. On production server
git pull
mf db migrate  # Apply approved migrations

# 3. Verify
# Check database schema matches expectations
```

### Choosing Drivers
- **Local Development**: SQLite (simplest, no setup)
- **CI/CD Testing**: SQLite or PostgreSQL test instance
- **Production**: PostgreSQL (or MySQL with future driver)
- **Data Migration**: Use driver matching target database

## Troubleshooting

### "Unknown driver: mysql"
```bash
# Solution: Use PostgreSQL or wait for MySQL driver
# Check registered drivers:
python -c "from src.corplang.executor.db.drivers.registry import DRIVERS; print(list(DRIVERS.keys()))"
```

### "ALTER not supported"
```bash
# SQLite limitation with ALTER/DROP COLUMN
# Workaround 1: Use PostgreSQL for development
# Workaround 2: Recreate database from scratch
# Workaround 3: Wait for table rebuild implementation
```

### "Type mismatch in generated SQL"
```bash
# Check field type mapping in driver:
# src/corplang/executor/db/drivers/your_driver.py

# Example:
from src.corplang.executor.db.drivers.sqlite import SQLiteDriver
field = {'type': 'DecimalField', 'params': [10, 2], 'kwargs': {}}
print(SQLiteDriver.get_field_type(field))  # Should show: NUMERIC(10,2)
```
