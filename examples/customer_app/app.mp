// Customer management app

import db

db.connect("sqlite://app.db")

User.create(name="Alice", email="alice@test.com")
User.create(name="Bob", email="bob@test.com")

var users = User.objects.all()
for (var u in users) {
    print(u.name, u.email)
}
