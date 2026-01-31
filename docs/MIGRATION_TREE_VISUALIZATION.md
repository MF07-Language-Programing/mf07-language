# Tree Visualization for Database Migrations

Quando você executa `mf db makemigrations` ou `mf db migrate`, uma árvore visual clara é exibida mostrando:

## Exemplos de Saída

### 1️⃣ Descoberta de Modelos (`makemigrations`)

```
Models Discovered
├── File: models.mp
│   ├── Model: Order -> table 'orders'
│   │   ├── id: AutoField [primary_key=True]
│   │   ├── status: CharField
│   │   ├── total: DecimalField
│   │   └── user_id: ForeignKey
│   └── Model: User -> table 'users'
│       ├── created_at: DateTimeField
│       ├── email: CharField [unique=True]
│       ├── id: AutoField [primary_key=True]
│       └── name: CharField
```

**O que você vê:**
- Arquivo onde o modelo foi encontrado
- Nome do modelo e tabela mapeada (usando arrows)
- Cada campo com seu tipo
- [primary_key=True] = Chave primária
- [unique=True] = Campo único
- [null=True] = Permite valores nulos

### 2️⃣ Operações de Migração (`makemigrations` + `migrate`)

```
Migration Operations
├── Add Column
│   └── Table 'users' - Field 'phone'
│       ├── type: VARCHAR(20)
│       └── null: True
├── Alter Column
│   └── Table 'orders' - Field 'total'
│       ├── type: DECIMAL(10,2)
│       └── default: 0.00
└── Create Table
    ├── Table: 'users' (model User)
    │   ├── created_at: TIMESTAMP
    │   ├── email: TEXT
    │   ├── id: INTEGER [primary_key=True]
    │   └── name: TEXT
    └── Table: 'orders' (model Order)
        ├── id: INTEGER [primary_key=True]
        ├── status: TEXT
        ├── total: REAL
        └── user_id: INTEGER
```

**O que você vê:**
- Create Table - Novas tabelas sendo criadas
- Add Column - Novos campos sendo adicionados
- Alter Column - Campos sendo modificados
- Drop Column - Campos sendo removidos
- Create Index - Índices sendo criados
- Drop Index - Índices sendo removidos

Cada operação mostra:
- Nome exato da tabela e coluna
- Tipo de dado
- Constraints (primary_key, unique, null)
- Valores padrão

## Como Funciona

### Fluxo Completo de Migrações

```bash
# 1. Gera plano a partir dos modelos (mostra árvore de descoberta)
mf db makemigrations

# 2. Aplica as migrações (mostra árvore de operações)
mf db migrate
```

### Exemplo Real

```bash
$ mf db makemigrations

Models Discovered
└── File: models.mp
    ├── Model: User -> table 'users'
    │   ├── id: AutoField [primary_key=True]
    │   ├── name: CharField
    │   └── email: CharField [unique=True]
    └── Model: Order -> table 'orders'
        ├── id: AutoField [primary_key=True]
        ├── user_id: ForeignKey
        └── total: DecimalField

Migration Operations
└── Create Table
    ├── Table: 'users' (model User)
    │   ├── id: INTEGER [primary_key=True]
    │   ├── name: TEXT
    │   └── email: TEXT
    └── Table: 'orders' (model Order)
        ├── id: INTEGER [primary_key=True]
        ├── user_id: INTEGER
        └── total: REAL

✓ Migrations generated: migrations/plan.initial.json

$ mf db migrate

Using database: sqlite://./app.db

Migration Operations:
Migration Operations
└── Create Table
    ├── Table: 'users' (model User)
    │   ├── id: INTEGER [primary_key=True]
    │   ├── name: TEXT
    │   └── email: TEXT
    └── Table: 'orders' (model Order)
        ├── id: INTEGER [primary_key=True]
        ├── user_id: INTEGER
        └── total: REAL

✓ Applied migrations to sqlite://./app.db
```

## Símbolos Usados

| Símbolo | Significado |
|---------|-----------|
| `├──` | Ramo intermediário (não é o último) |
| `└──` | Ramo final (é o último) |
| `│` | Linha vertical (conexão) |
| `-` | Adição |
| `+` | Novo campo |
| `~` | Campo modificado |
| `+` | Prefixo para novos |
| `-` | Prefixo para removidos |

## Constraints Exibidos

| Constraint | Significado |
|-----------|-----------|
| `primary_key=True` | Chave primária |
| `unique=True` | Campo único |
| `null=True` | Permite NULL |

## Estrutura de Diretórios

```
seu_projeto/
├── models.mp                    # Define os modelos
├── language_config.yaml         # Configuração (database + outros)
├── migrations/
│   ├── schema.json              # Snapshot do schema
│   └── plan.initial.json        # Plano de operações
└── seu_codigo.mp
```

## Benefícios

✓ **Clareza** - Veja exatamente o que será migrado
✓ **Controle** - Identifique mudanças antes de aplicar
✓ **Rastreabilidade** - Saiba qual arquivo gerou qual modelo
✓ **Profissionalismo** - Visual limpo e direto, sem distrações
✓ **Compatibilidade** - Similar ao Django, familiar para devs

