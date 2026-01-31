# Migration Strategy - Sequential File-Based System

## Overview

The migration system now uses **sequential numbered files** instead of overwriting a single plan file. This allows you to:

1. Generate multiple migrations without applying them immediately
2. Apply migrations in strict order
3. Track which migrations have been applied via `.applied` metadata file
4. Never lose migration history

## How It Works

### Migration File Naming

Each migration gets a sequential filename with a descriptive suffix:

```
migrations/
  001_enum_invoicestatus_enum_userrole.json    # Initial enum creation
  002_add_phone.json                            # Added phone column
  003_add_discount_cents.json                   # Added discount field
  schema.json                                   # Current schema snapshot
  .applied                                      # Applied migrations tracker
```

### Automatic Naming Rules

Migration names are generated from the operations they contain:

- `create_<model>` - New model creation
- `add_<field>` - Column addition
- `drop_<field>` - Column removal
- `alter_<field>` - Column modification
- `enum_<name>` - Enum type creation
- `fk_<field>` - Foreign key constraint
- `drop_<model>` - Model/table removal

## Workflow

### 1. Generate Migrations

```bash
mf db makemigrations
```

Creates a new migration file for changes detected:

```
✓ Migrations generated: migrations/002_add_phone.json
```

**Important**: This does **not** apply the migration to the database yet.

### 2. Apply Migrations in Sequence

```bash
mf db migrate
```

Applies **all unapplied migrations in order**:

```
✓ Applied 2 migration(s):
  ✓ 001_enum_invoicestatus_enum_userrole.json
  ✓ 002_add_phone.json
```

### 3. Track Applied Migrations

The `.applied` file tracks which migrations have been executed:

```json
{
  "applied": [
    "001_enum_invoicestatus_enum_userrole.json",
    "002_add_phone.json"
  ]
}
```

Subsequent `migrate` calls only apply new migrations:

```bash
mf db makemigrations  # Creates 003_add_discount_cents.json
mf db migrate         # Only applies 003_add_discount_cents.json
```

## Real-World Scenario

### Situation: Multiple Changes Before Migration

You make two changes to your models without running migrate in between:

```bash
# Change 1: Add phone field to Customer
# $ mf db makemigrations
# → Creates 002_add_phone.json

# Change 2: Add discount field to Invoice
# $ mf db makemigrations
# → Creates 003_add_discount_cents.json

# Now apply ALL pending migrations in order
$ mf db migrate
✓ Applied 2 migration(s):
  ✓ 002_add_phone.json
  ✓ 003_add_discount_cents.json
```

This ensures:
- Both migrations are tracked
- Applied in strict sequence (002 before 003)
- Neither overwrites the other
- Full audit trail is preserved

## Reset Migrations

Remove all migration files and optionally drop database objects:

```bash
# Remove only migration files
mf db reset

# Also drop all tables/enums from the database
mf db reset --drop-db
```

## File Structure Example

After three iterations:

```
migrations/
├── 001_enum_invoicestatus_enum_userrole.json
│   └── Operations: create_enum InvoiceStatus, create_enum UserRole
├── 002_add_phone.json
│   └── Operations: add_column phone to lt_customers
├── 003_add_discount_cents.json
│   └── Operations: add_column discount_cents to lt_invoices
├── schema.json
│   └── Current schema state (enums, models, relations)
└── .applied
    └── {"applied": ["001_...", "002_...", "003_..."]}
```

## Benefits

✅ **No overwrites**: Each change is preserved  
✅ **Clear history**: Filenames show what changed  
✅ **Idempotent**: Running migrate multiple times is safe  
✅ **Auditable**: Full trail of all migrations  
✅ **Sequential**: Strict ordering prevents schema conflicts  
✅ **Reversible**: Can inspect old migrations anytime  

## Database Drift Detection

Currently, the system:
- Compares **models.mp** against the last snapshot (schema.json)
- Generates incremental migrations for differences
- Does **not** introspect the live database

If your database has manual changes or diverges from migrations, recommend:
1. Backup your database
2. `mf db reset --drop-db` (caution!)
3. `mf db makemigrations && mf db migrate` (rebuild schema from models)

## Supported Drivers

- **SQLite**: File-based, development/testing
- **PostgreSQL**: Server-based, production-ready

See `language_config.yaml` for driver and DSN configuration.
