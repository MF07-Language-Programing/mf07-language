enum OrderStatus {
    PENDING,
    IN_PROGRESS,
    FINISHED,
    CANCELED
}

model Order extends Model {
    id = AutoField()
    user = ForeignKey(User)
    status = EnumField(OrderStatus, default=OrderStatus.PENDING)
    total = DecimalField(10, 2)
    description = TextField()
    quantity = IntegerField(default=1)
    created_at = DateTimeField(auto_now_add=true)
    updated_at = DateTimeField(auto_now=true)

    table = "orders"
}
