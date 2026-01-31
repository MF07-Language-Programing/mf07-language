// Customer management app
// Database is auto-connected from language_config.yaml
from models import User
import db

// Optional: if language_config.yaml is not configured,
// you can manually connect here:
// db.connect("sqlite://./app.db")

User.create(name="Alice", email="alice@test.com")
User.create(name="Bob", email="bob@test.com")

var users = User.objects.all()
print(f"Users: {type(users)}")
for (var u in users) {
    print(u.name, u.email)
}
