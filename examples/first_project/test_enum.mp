import console from core.utils.logger
import db

enum UserRole {
    ADMIN,
    CUSTOMER,
    STAFF
}

enum Status {
    PENDING = "pending",
    ACTIVE = "active",
    INACTIVE = "inactive"
}

model User extends Model {
    id = AutoField()
    name = CharField(100)
    role = EnumField(UserRole, default=UserRole.CUSTOMER)
    status = EnumField(Status, default=Status.PENDING)
    table = "users"
}

# Connect to database
db.connect("sqlite://test_enum.db")

# Create user with enum values
var user1 = User.create(
    name="Alice",
    role=UserRole.ADMIN,
    status=Status.ACTIVE
)

console.info("Created user:", user1)
console.info("Role type:", user1.role)
console.info("Role name:", user1.role.name)
console.info("Role value:", user1.role.value)

# Query users
var users = User.objects.all()
console.info("Total users:", users.length)

# Filter by enum
var admins = User.objects.filter(role=UserRole.ADMIN)
console.info("Admin users:", admins.length)
