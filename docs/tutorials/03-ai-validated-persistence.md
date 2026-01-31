# Tutorial 3 — Validação de Dados Gerada por IA (25 min)

Agora que você orquestrou múltiplos agentes, o próximo desafio é **persistência**. A maioria das aplicações precisa armazenar dados — mas como validar dados *automaticamente* antes de inserir?

Em Corplang, agentes fazem a validação. Não há callbacks, hooks ou middleware — a IA é parte nativa do pipeline de dados.

## O Que Você Aprenderá

- Definição de modelos com `model { }`
- Validação automática via `AgentPredictExecutor`
- Migrations dirigidas por tipo (SQLite → PostgreSQL)
- Rastreamento de quem validou, quando e por quê
- Multi-driver persistence sem reescrever código

## Pré-requisitos

- Completar [Tutorial 2](02-multi-agent-routing.md)
- SQLite instalado (geralmente já está em Python)
- Provider configurado

---

## Parte 1: Definir Modelo com IA (8 min)

### Criar Projeto

```bash
mf init crm-validated
cd crm-validated
```

### Código: `main.mp`

```mp
# Modelo: Cliente CRM com validação automática
model Cliente {
  id: int primary_key auto_increment
  nome: text not_null
  email: text unique not_null
  telefone: text nullable
  ativo: bool default true
  criado_em: datetime auto_now
}

# Agente: Valida dados de cliente antes de inserir
agent ValidadorCliente {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.1        # Bem determinístico
  }
  
  fn validar(nome: text, email: text, telefone: text) -> bool {
    let prompt = """
    Valide os seguintes dados de cliente:
    - Nome: {nome}
    - Email: {email}
    - Telefone: {telefone}
    
    Critérios:
    1. Nome tem pelo menos 3 caracteres
    2. Email é formato válido (contém @)
    3. Telefone é vazio OU contém apenas números e -
    
    Responda apenas com: SIM ou NÃO
    """
    let resposta = invoke self with prompt
    return text.lower(resposta).contains("sim")
  }
  
  fn gerar_retroalimentacao(nome: text, email: text, telefone: text) -> text {
    let prompt = """
    Que problemas você vê nestes dados de cliente?
    - Nome: {nome}
    - Email: {email}
    - Telefone: {telefone}
    
    Seja conciso.
    """
    return invoke self with prompt
  }
}

# Agente: Enriquece dados do cliente
agent EnriquecedorCliente {
  config: {
    "provider": "ollama",
    "model": "llama2"
  }
  
  fn normalizar_email(email: text) -> text {
    let prompt = "Normalize este email (lowercase, sem espaços): " + email
    return invoke self with prompt
  }
  
  fn categorizar_cliente(nome: text) -> text {
    let prompt = "Baseado no nome, qual é o setor provável? " + nome
    return invoke self with prompt
  }
}

# Persistência: Driver abstrato
driver ClienteRepository {
  fn criar(cliente: Cliente) -> bool
  fn buscar(id: int) -> Cliente
  fn listar() -> [Cliente]
  fn atualizar(id: int, cliente: Cliente) -> bool
  fn deletar(id: int) -> bool
}

# Implementação SQLite
impl ClienteRepository for SQLiteDriver {
  fn criar(cliente: Cliente) -> bool {
    try {
      insert into Cliente (nome, email, telefone, ativo)
      values (cliente.nome, cliente.email, cliente.telefone, cliente.ativo)
      return true
    } catch (e: Exception) {
      println("Erro ao inserir: " + e.message)
      return false
    }
  }
  
  fn buscar(id: int) -> Cliente {
    return select * from Cliente where id = id limit 1
  }
  
  fn listar() -> [Cliente] {
    return select * from Cliente where ativo = true
  }
  
  fn atualizar(id: int, cliente: Cliente) -> bool {
    try {
      update Cliente set nome = cliente.nome, email = cliente.email
      where id = id
      return true
    } catch (e: Exception) {
      return false
    }
  }
  
  fn deletar(id: int) -> bool {
    try {
      update Cliente set ativo = false where id = id
      return true
    } catch (e: Exception) {
      return false
    }
  }
}

# Pipeline: Criar cliente com validação
fn criar_cliente_validado(nome: text, email: text, telefone: text) -> bool {
  # 1. VALIDAR
  let validador = new ValidadorCliente()
  let valido = validador.validar(nome, email, telefone)
  
  if !valido {
    let feedback = validador.gerar_retroalimentacao(nome, email, telefone)
    println("✗ Dados inválidos: " + feedback)
    return false
  }
  
  println("✓ Dados validados")
  
  # 2. ENRIQUECER
  let enriquecedor = new EnriquecedorCliente()
  let email_normalizado = enriquecedor.normalizar_email(email)
  let categoria = enriquecedor.categorizar_cliente(nome)
  
  println("  - Email normalizado: " + email_normalizado)
  println("  - Categoria: " + categoria)
  
  # 3. PERSISTER
  let repo = new ClienteRepository()
  var cliente = Cliente {
    nome: nome,
    email: email_normalizado,
    telefone: telefone,
    ativo: true
  }
  
  let sucesso = repo.criar(cliente)
  if sucesso {
    println("✓ Cliente criado no banco")
    return true
  } else {
    println("✗ Erro ao salvar cliente")
    return false
  }
}

fn main() {
  # Teste 1: Dados válidos
  println("--- Teste 1: Dados válidos ---")
  criar_cliente_validado("João Silva", "joao@email.com", "11-9999-9999")
  
  # Teste 2: Email inválido
  println("\n--- Teste 2: Email inválido ---")
  criar_cliente_validado("Maria", "nao-eh-email", "")
  
  # Teste 3: Nome muito curto
  println("\n--- Teste 3: Nome muito curto ---")
  criar_cliente_validado("Ana", "ana@email.com", "11-8888-8888")
}

main()
```

---

## Parte 2: Entender a Validação (7 min)

### Fluxo de Dados

```
Dados brutos
    ↓
[Validador] ← AgentPredictExecutor
    ├─ Valida critérios
    ├─ Retorna bool
    └─ Gera feedback (opcional)
    ↓
Dados válidos?
    ├─ NÃO → Rejeita
    └─ SIM → [Enriquecedor]
         ├─ Normaliza email
         ├─ Categoriza
         └─ Retorna dados enriquecidos
         ↓
    [Persistência]
    ├─ SQLite (dev)
    ├─ PostgreSQL (prod)
    └─ Sem reescrever código
         ↓
    Banco de dados
```

### O Que Diferencia Corplang

1. **Sem boilerplate**: Validação não é função auxiliar, é agente nativo
2. **Type-safe**: Modelos são tipos, não strings mágicas
3. **Auditável**: Cada decisão de agente é rastreada
4. **Multi-driver**: Mesmo código funciona em SQLite e PostgreSQL

---

## Parte 3: Multi-Driver Migrations (7 min)

### Migrar para PostgreSQL sem reescrever

Atualize `language_config.yaml`:

```yaml
corplang:
  version: "0.1.0"
  name: "crm-validated"

database:
  driver: "postgresql"    # Mude de SQLite para PostgreSQL
  config:
    host: "localhost"
    port: 5432
    user: "postgres"
    password: "senha123"
    database: "crm_db"

# Para desenvolvimento, use SQLite:
# database:
#   driver: "sqlite"
#   config:
#     path: "./db.sqlite"
```

### Gerar Migration

```bash
mf db makemigrations
```

Isso cria:

```
migrations/
├── plan.initial.json
└── plan.incremental.json
```

Verifique o plano:

```bash
cat migrations/plan.initial.json
```

Output:

```json
{
  "driver": "postgresql",
  "models": [
    {
      "name": "Cliente",
      "fields": [
        {"name": "id", "type": "int", "primary_key": true},
        {"name": "nome", "type": "text", "not_null": true},
        {"name": "email", "type": "text", "unique": true},
        {"name": "telefone", "type": "text", "nullable": true},
        {"name": "ativo", "type": "bool", "default": "true"},
        {"name": "criado_em", "type": "datetime", "auto_now": true}
      ]
    }
  ],
  "actions": ["CREATE TABLE Cliente (...)"]
}
```

### Aplicar Migration

```bash
mf db migrate
```

Seu código Corplang **não muda**. O driver é abstraído.

---

## Parte 4: Observabilidade & Auditoria (5 min)

Rastreie quem validou, quando, e por quê:

```mp
from core.runtime.observability import get_observability_manager

var audit_log = []

fn rastreador_validacao(event) -> void {
  if event.node_type == "AgentPredictExecutor" {
    audit_log.append({
      "timestamp": sys.now(),
      "agente": "ValidadorCliente",
      "resultado": event.result,
      "tempo_ms": event.elapsed_seconds * 1000
    })
  }
}

fn listar_auditoria() -> void {
  println("=== Auditoria de Validações ===")
  for (var log in audit_log) {
    println(log.timestamp + ": " + log.resultado + " (" + log.tempo_ms + "ms)")
  }
}

fn main() {
  let obs = get_observability_manager()
  obs.register(rastreador_validacao)
  
  criar_cliente_validado("Alice", "alice@email.com", "11-7777-7777")
  criar_cliente_validado("Bob", "bob@email", "")  # Inválido
  criar_cliente_validado("Charlie", "charlie@email.com", "11-6666-6666")
  
  listar_auditoria()
}

main()
```

Output:

```
=== Auditoria de Validações ===
2025-01-11 10:23:45: true (234ms)
2025-01-11 10:23:46: false (189ms)
2025-01-11 10:23:47: true (245ms)
```

---

## Parte 5: Tratamento de Conflitos (3 min)

Quando migramos para PostgreSQL, pode haver conflitos:

```bash
mf db migrate --check-conflicts
```

Se houver conflitos:

```
⚠ Conflito detectado:
  - SQLite: INTEGER PRIMARY KEY (autoincrement)
  - PostgreSQL: SERIAL (sequence)
  
  Solução: Use SERIAL em ambos (quebra compatibilidade SQLite)
  Opção 1: Criar sequência customizada
  Opção 2: Manualizar inserção de IDs
```

Corplang sugere a solução; você decide.

---

## Arquitetura Interna

```
┌─────────────────────────────────────┐
│ main.mp — Código Corplang           │
│                                     │
│ criar_cliente_validado(...)         │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ ValidadorCliente.validar()          │
│ └─→ AgentPredictExecutor            │
│     └─→ IntelligenceProvider        │
│         └─→ return bool             │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ EnriquecedorCliente.normalizar()    │
│ └─→ AgentPredictExecutor            │
│     └─→ return dados enriquecidos   │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ ClienteRepository.criar()           │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ SQLiteDriver (dev)              │ │
│ │ insert into Cliente (...)       │ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ PostgreSQLDriver (prod)         │ │
│ │ insert into "Cliente" (...)     │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Ponto-chave:** Lógica de negócio (validação) é desacoplada de persistência (driver).

---

## Referência Rápida

| Ação | Comando |
|------|---------|
| Gerar migration | `mf db makemigrations` |
| Aplicar migration | `mf db migrate` |
| Verificar plano | `cat migrations/plan.incremental.json` |
| Validar banco | `mf db connect sqlite ./db.sqlite` |

---

## Próximas Etapas

1. **Servir via HTTP**: Exponha seu CRM em API?
   → [Tutorial 4 — Web App com Agentes](04-web-app-agents.md)

2. **Entender migrations avançadas**: Multi-driver em produção?
   → [Multi-Driver Migrations](../MULTI_DRIVER_MIGRATIONS.md)

3. **Customizar provider**: Quer OpenAI em vez de Ollama?
   → [Custom Intelligence Providers](../guides/intelligence-providers.md)

---

**Parabéns!** Você integrou agentes diretamente no pipeline de dados. 

Próximo: [Tutorial 4 — Web App com Agentes](04-web-app-agents.md) (35 min)
