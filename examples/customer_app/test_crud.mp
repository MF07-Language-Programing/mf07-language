// Test CRUD read API
import db

db.connect("sqlite://app.db")

print("=== All Users ===")
print("Count:", User.objects.count())
print("Exists:", User.objects.exists())

print("\n=== Get with Filter ===")
var alice = User.objects.filter(name="Alice").get()
print("Got Alice:", alice.name, alice.email)

print("\n=== Filter + Count ===")
var alice_count = User.objects.filter(name="Alice").count()
print("Alice count:", alice_count)

print("\n=== Filter + Exists ===")
var bob_exists = User.objects.filter(name="Bob").exists()
print("Bob exists:", bob_exists)

var unknown_exists = User.objects.filter(name="Unknown").exists()
print("Unknown exists:", unknown_exists)

print("\n=== Get + Filter (Django-style) ===")
var bob = User.objects.filter(email="bob@test.com").get()
print("Got Bob:", bob.name, bob.email)
