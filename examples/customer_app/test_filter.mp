// Test filtering
import db

db.connect("sqlite://app.db")

print("=== All Users ===")
var all = User.objects.all()
for (var u in all) {
    print("  ", u.id, u.name, u.email)
}

print("\n=== Filter: name=Alice ===")
var filtered = User.objects.filter(name="Alice")
for (var u in filtered) {
    print("  ", u.id, u.name, u.email)
}
