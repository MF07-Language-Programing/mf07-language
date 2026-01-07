# Customer App — ORM Example

Real .mp app using database ORM (Django-like API).

## Setup

```bash
# 1. Generate migrations
mf db makemigrations

# 2. Apply migrations to SQLite
mf db migrate

# 3. Run app
mf run app.mp
```

## Files

- `models.mp` — Model definitions (User extends BaseModel)
- `app.mp` — Main app (creates/lists users)
- `test_crud.mp` — Full CRUD read API (count, exists, get, filter)
- `test_filter.mp` — Query with filter
- `test_postgresql.mp` — PostgreSQL connection example (requires setup)

## API

```javascript
// Connect
import db
db.connect("sqlite://app.db")

// Create (INSERT)
var result = User.create(name="Alice", email="alice@test.com")

// Read (SELECT)
var users = User.objects.all()           // all rows
var one = User.objects.get()              // single row (error if 0 or >1)
var filtered = User.objects.filter(name="Alice")  // QuerySet

// Query operations
User.objects.count()                      // count all
User.objects.exists()                     // check any exists
User.objects.filter(email="a@b.com").count()    // count filtered
User.objects.filter(name="Alice").get()   // get filtered (error if 0 or >1)
User.objects.filter(name="Alice").exists() // check filtered exists

// Iterate
for (var u in User.objects.all()) {
    print(u.id, u.name, u.email)
}
```

## Supported Databases

- **SQLite**: `sqlite://path/to/file.db` (default, no deps)
- **PostgreSQL**: `postgresql://user:pass@host/db` (requires psycopg2)
  - URL variants: `postgresql://...` or `postgres://...`

## Model Definition

```javascript
model User extends BaseModel {
    id = AutoField()
    name = CharField(120)
    email = CharField(120)
    
    table = "users"  // optional; defaults to snake_case plural
}
```

## Testing

```bash
# Test full CRUD API
mf run test_crud.mp

# Test filtering
mf run test_filter.mp

# Test PostgreSQL (setup required)
mf run test_postgresql.mp
```

## Notes

- `BaseModel` is the marker class for all models
- ORM auto-loads models from `models.mp` when `import db`
- Migrations are schema-only (SQLite/PostgreSQL compatible DDL)
- No transaction support yet (future)

