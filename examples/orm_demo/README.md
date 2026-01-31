# ORM Demo Project

Example of using the Corplang ORM with centralized database configuration.

## Files

- `models.mp` - Define your data models
- `main.mp` - Use models with auto-connected database
- `language_config.yaml` - Centralized configuration

## Setup

1. Configure the database in `language_config.yaml`:

```yaml
database:
  driver: "sqlite"
  dsn: "./demo.db"
```

2. Define your models in `models.mp`

3. Generate migrations:

```bash
mf db makemigrations
```

4. Apply migrations:

```bash
mf db migrate
```

5. Run your application:

```bash
mf run main.mp
```

## Usage Example

```mp
from models import User, Order
import db

// Auto-connected via language_config.yaml
// No need to call db.connect()

// Create records
User.create(name="Alice", email="alice@example.com")
Order.create(user_id=1, total=99.99)

// Query records
var users = User.objects.all()
var my_order = Order.objects.filter(user_id=1).get()

print(my_order)
```
