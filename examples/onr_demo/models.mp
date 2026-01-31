enum InvoiceStatus {
    DRAFT,
    PENDING,
    PAID,
    CANCELED
}

enum UserRole {
    ADMIN,
    CUSTOMER,
    EMPLOYED,
    STAFF
}

model Customer extends Model {
    id = AutoField()
    email = CharField(max_length=255, unique=true)
    name = CharField(max_length=999)
    phone = CharField(max_length=20, null=true)
    signup_at = DateTimeField(auto_now_add=true)
    is_active = BooleanField(default=true)
    role = EnumField(UserRole, default=UserRole.ADMIN)

    table = "lt_customers"
}

model Invoice extends Model {
    id = AutoField()
    customer = ForeignKey(Customer)
    total_cents = IntegerField()
    currency = CharField(max_length=4)
    discount_cents = IntegerField(default=0)
    status = EnumField(InvoiceStatus, default=InvoiceStatus.DRAFT)
    created_at = DateTimeField(auto_now_add=true)
    text = TextField(null=true)

    table = "lt_invoices"
}
