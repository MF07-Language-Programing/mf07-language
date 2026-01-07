// Test PostgreSQL connection (needs psycopg2 and running PG server)
// 
// Setup (Linux/Mac):
// 1. Install psycopg2: pip install psycopg2-binary
// 2. Start PostgreSQL service
// 3. Create database: createdb mf_test
// 4. Run this file

import db

// Connect to local PostgreSQL
db.connect("postgresql://postgres:postgres@localhost:5432/mf_test")

print("=== Connected to PostgreSQL ===")

// Create users (table must exist first via migrations)
User.create(name="Charlie", email="charlie@test.com")
User.create(name="Diana", email="diana@test.com")

// List all
print("\n=== All Users ===")
var users = User.objects.all()
for (var u in users) {
    print("  ", u.id, u.name, u.email)
}

// Query
print("\n=== Count & Filter ===")
print("Total:", User.objects.count())
print("Charlie exists:", User.objects.filter(name="Charlie").exists())
