# ORM Implementation Checkpoint

## ✅ Prioridade 1: CRUD Read API (COMPLETA)

**Métodos implementados:**

### ModelManager

- `Model.objects.all()` → List[Dict]
- `Model.objects.filter(**kwargs)` → QuerySet  
- `Model.objects.count()` → int
- `Model.objects.exists()` → bool
- `Model.objects.get(**kwargs)` → Dict (error if 0 or >1)

### QuerySet

- `qs.all()` → List[Dict]
- `qs.filter(**kwargs)` → QuerySet (chainable)
- `qs.get()` → Dict (error if 0 or >1)
- `qs.count()` → int
- `qs.exists()` → bool

**Teste:** `mf run test_crud.mp`

```
Count: 2
Exists: True
Got Alice: Alice alice@test.com
Alice count: 1
Bob exists: True
Unknown exists: False
Got Bob: Bob bob@test.com
```

---

## ✅ Prioridade 2: BaseModel Explícito (COMPLETA)

**Model definition:**

```javascript
model User extends BaseModel {
    id = AutoField()
    name = CharField(120)
    email = CharField(120)
    table = "users"
}
```

**Parser atualizado:** Aceita `extends BaseModel` ou `extends Model`

**Runtime:** BaseModel registrado como builtin global

---

## ✅ Prioridade 3: Metadata (PARCIAL)

- `table = "name"` funciona
- Parser extrai corretamente
- Default snake_case plural não implementado (ainda usa `table = "..."` obrigatório)

---

## ✅ Prioridade 4: PostgreSQL REAL (PRONTO)

**Estrutura:**

- Placeholders corretos: `?` para SQLite, `%s` para PostgreSQL
- Driver detecção: `conn.driver` propaga para QuerySet
- INSERT/SELECT com placeholders dinâmicos

**Suportado:**

- `sqlite://path/to/db`
- `postgresql://user:pass@host/db`
- `postgres://...` (alias)

**Não testado em produção** (exige servidor PG)

**Preparação:** `mf run test_postgresql.mp` (requer setup)

---

## Checkpoint: "Sin pensar en cómo funciona"

```javascript
import db
db.connect("postgresql://postgres:postgres@localhost/postgres")
users = User.objects.filter(email="alice@test.com")
print(users)
```

**Status:** Funciona em SQLite (100%). PostgreSQL estruturalmente pronto (placeholder handling + driver detection implementado).

---

## Próxima Fase (não fazer agora)

- Joins automáticos
- select_related / prefetch_related
- Query builder complexo
- Transactions sofisticadas
- Enum nativo
- Reversão de migrations

**Armazém de avanço incremental criado.** Sistema é produto, não prototype.
