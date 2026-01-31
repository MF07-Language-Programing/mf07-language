enum OrderStatus {
    PENDING,
    IN_PROGRESS,
    FINISHED,
    CANCELED
}

model User extends Model {
    id = AutoField()
    name = CharField(max_length=100)
    email = CharField(max_length=255)
    phone = CharField(max_length=20, null=true)
    created_at = DateTimeField(auto_now_add=true)

    table = "users"
}

model Order extends Model {
    id = AutoField()
    user = ForeignKey(User)
    status = EnumField(OrderStatus, default=OrderStatus.PENDING)
    total = DecimalField(12, 2)
    description = TextField()
    quantity = IntegerField(default=1)
    created_at = DateTimeField(auto_now_add=true)
    updated_at = DateTimeField(auto_now=true)
    is_paid = BooleanField(default=false)

    table = "orders"
}
