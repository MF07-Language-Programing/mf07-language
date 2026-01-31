// Load-test seeder: cria muitos registros e valida que migrations preservam dados
from models import Customer, Invoice, InvoiceStatus
import db

// Ajuste estes valores conforme necessário
var CUSTOMER_COUNT = 2000
var INVOICES_PER_CUSTOMER = 2

// Se não quiser usar language_config.yaml, descomente e ajuste o DSN abaixo
// db.connect("postgresql://postgres:postgres@localhost:5432/mf_test")

print(f"Iniciando seed: {CUSTOMER_COUNT} clientes x {INVOICES_PER_CUSTOMER} faturas")

var createdCustomers = 0
var createdInvoices = 0

var i = 0
while(i < CUSTOMER_COUNT) {
    var name = f"Customer {i}"
    var email = f"customer{i}@loadtest.local"
    var active = (i % 5) != 0

    var customer: Customer = Customer.create(name=name, email=email, is_active=active)
    createdCustomers = createdCustomers + 1
    var cid = Customer.objects.filter(email=email).get().id

    var j = 0
    while(j < INVOICES_PER_CUSTOMER) {
        var cents = (i * 137 + j * 53) % 500000 + 100
        var status = "PENDING"
        if(j % 3 == 0) {
            status = "PAID"
        }
        Invoice.create(customer=cid, total_cents=cents, currency="USD", status=status)
        createdInvoices = createdInvoices + 1
        j = j + 1
    }

    if(i > 0 and i % 500 == 0) {
        print(f"Seed em progresso: {i} clientes inseridos...")
    }

    i = i + 1
}

print(f"Seed concluído: clientes criados={createdCustomers}, faturas criadas={createdInvoices}")
print("Para testar migrations com dados existentes:\n  1) rode `python ../../mf db makemigrations`\n  2) rode `python ../../mf db migrate`\n  3) altere models.mp e repita para validar ALTER/DROP/ADD com dados reais")
