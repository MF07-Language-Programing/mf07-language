// ORM Demo models (Django-like DX)

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
    created_at = DateTimeField(auto_now_add=true)

    table = "orders"
}
