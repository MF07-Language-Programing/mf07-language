// Customer management models

model User extends BaseModel {
    id = AutoField()
    name = CharField(120)
    whatsapp = CharField(120)
    email = CharField(120)

    table = "users"
}

