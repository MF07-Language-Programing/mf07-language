# AI-Generated Schemas: Validação e Persistência Integradas

## Visão Geral

Corplang unifica validação de dados com persistência através de **AgentPredictExecutor**. Em vez de ter camadas separadas (validation → ORM → database), agentes nativos validam dados antes de inserir — transformando o pipeline tradicional em um fluxo de "decisão".

Este documento mostra como:
1. Agentes validam dados em tempo real
2. Schemas evoluem baseado em decisões de agentes
3. Migrações rastreiam decisões de IA
4. Multi-driver persistence funciona com validação automática

---

## Arquitetura: Decision → Validation → Persistence

### Fluxo Tradicional (sem IA)

```
Input
  ↓
Validate (regras hardcoded)
  ↓
Transform (ORM)
  ↓
Insert (database)
```

### Fluxo Corplang (com IA)

```
Input
  ↓
[AgentValidator] ← IntelligenceProvider
  ├─ Aprova/Rejeita
  ├─ Normaliza
  ├─ Enriquece
  └─ Retorna decisão com metadados
  ↓
[Decisão Auditada]
  ├─ Quem validou (agente)
  ├─ Quando (timestamp)
  ├─ Por quê (motivo/score)
  └─ Contexto (user_id, department, etc)
  ↓
Insert (com auditoria)
  ↓
Banco de Dados
  ├─ Dados + Metadata
  └─ Completamente rastreável
```

---

## Exemplo 1: Validação de Email com Agente

### Schema (Corplang Model)

```mp
model Usuario {
  id: int primary_key auto_increment
  email: text unique not_null
  nome: text not_null
  dominio_empresa: text nullable          # Extraído por agente
  categoria: text default "standard"      # Definido por agente
  validado_em: datetime nullable          # Preenchido por agente
  validador: text nullable                # Quem validou
}
```

### Agente de Validação

```mp
agent ValidadorEmail {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.1
  }
  
  fn validar(email: text) -> {
    valido: bool,
    motivo: text,
    dominio: text
  } {
    let prompt = """
    Valide este email:
    {email}
    
    Critérios:
    1. Contém @
    2. Formato válido
    3. Domínio não é bloqueado (gmail.com, yahoo.com OK, temp-mail não)
    
    Responda JSON:
    {
      "valido": true/false,
      "motivo": "breve explicação",
      "dominio": "empresa.com"
    }
    """
    
    let resposta = invoke self with prompt
    return json.parse(resposta)
  }
  
  fn categorizar_usuario(email: text, nome: text) -> text {
    let prompt = """
    Baseado no email e nome, qual é a categoria do usuário?
    Email: {email}
    Nome: {nome}
    
    Opções: premium | standard | free | trial
    Responda com APENAS a categoria.
    """
    return invoke self with prompt
  }
}

# Usar agente em pipeline
fn criar_usuario_validado(email: text, nome: text) -> bool {
  let validador = new ValidadorEmail()
  
  # 1. Validar
  let resultado = validador.validar(email)
  if !resultado.valido {
    println("✗ Email inválido: " + resultado.motivo)
    return false
  }
  
  # 2. Categorizar
  let categoria = validador.categorizar_usuario(email, nome)
  
  # 3. Criar usuário com dados enriquecidos
  var usuario = Usuario {
    email: email,
    nome: nome,
    dominio_empresa: resultado.dominio,
    categoria: categoria,
    validado_em: sys.now(),
    validador: "ValidadorEmail"
  }
  
  # 4. Salvar
  let repo = new UsuarioRepository()
  return repo.criar(usuario)
}
```

---

## Exemplo 2: Esquemas que Evoluem com Agentes

### Cenário: Adicionar Novos Campos Baseado em Decisões

Imagine seu agente começa a extrair novos dados:

**Versão 1:**

```mp
model Cliente {
  id: int primary_key
  nome: text
  email: text
}
```

**O agente começa a categorizar clientes por segmento:**

```mp
# Agente nota que pode extrair segmento
# Developer avisa: "Adicione campo segmento"
model Cliente {
  id: int primary_key
  nome: text
  email: text
  segmento: text nullable  # ← Novo campo
}
```

**Gerar migration:**

```bash
mf db makemigrations
```

Output:

```
✓ Detecção de mudanças:
  └── Cliente model
      └── ADD COLUMN segmento text nullable
  
✓ Migrations generated: migrations/002_add_segmento_cliente.json
```

**Conteúdo da migration:**

```json
{
  "version": "0.1.0",
  "timestamp": "2025-01-11T10:30:00Z",
  "source": "AgentPredictExecutor",  // ← Origem: IA, não manual
  "driver": "postgresql",
  "operations": [
    {
      "type": "ALTER TABLE",
      "table": "Cliente",
      "action": "ADD COLUMN",
      "column": {
        "name": "segmento",
        "type": "text",
        "nullable": true
      }
    }
  ],
  "reason": "Agente categoriza clientes por segmento"
}
```

**Aplicar:**

```bash
mf db migrate
```

---

## Exemplo 3: Auditoria Completa de Decisões

### Modelo com Auditoria Integrada

```mp
model Pedido {
  id: int primary_key auto_increment
  cliente_id: int foreign_key not_null
  valor: decimal not_null
  moeda: text default "BRL"
  status: text default "pendente"
  
  # Auditoria de IA
  validador_agente: text                # Qual agente validou?
  score_confianca: int nullable         # Confiança (0-100)
  motivo_validacao: text nullable       # Por quê foi aprovado?
  rejeitado_em: datetime nullable       # Se foi rejeitado
  motivo_rejeicao: text nullable        # Por quê foi rejeitado?
  
  criado_em: datetime auto_now
  atualizado_em: datetime auto_now_update
}
```

### Agente que Popula Auditoria

```mp
agent ValidadorPedido {
  config: { "provider": "ollama", "model": "llama2" }
  
  fn validar_pedido(valor: decimal, moeda: text) -> {
    valido: bool,
    score: int,
    motivo: text
  } {
    let prompt = """
    Valide este pedido:
    Valor: {valor}
    Moeda: {moeda}
    
    Critérios:
    1. Valor > 0
    2. Moeda é válida (BRL, USD, EUR, etc)
    
    Retorne JSON:
    {
      "valido": true/false,
      "score": 1-100,
      "motivo": "breve explicação"
    }
    """
    
    let resultado = invoke self with prompt
    return json.parse(resultado)
  }
}

fn criar_pedido_auditado(cliente_id: int, valor: decimal, moeda: text) -> Pedido {
  let validador = new ValidadorPedido()
  let resultado = validador.validar_pedido(valor, moeda)
  
  var pedido = Pedido {
    cliente_id: cliente_id,
    valor: valor,
    moeda: moeda,
    validador_agente: "ValidadorPedido",
    score_confianca: resultado.score,
    motivo_validacao: resultado.motivo
  }
  
  if !resultado.valido {
    pedido.rejeitado_em = sys.now()
    pedido.motivo_rejeicao = resultado.motivo
    pedido.status = "rejeitado"
  }
  
  return pedido
}
```

**Query SQL resultante:**

```sql
INSERT INTO Pedido (
  cliente_id, valor, moeda,
  validador_agente, score_confianca, motivo_validacao,
  criado_em
) VALUES (
  123, 150.00, 'BRL',
  'ValidadorPedido', 95, 'Valor e moeda válidos',
  NOW()
);
```

**Auditoria:**

```bash
SELECT 
  id, valor, validador_agente, score_confianca, motivo_validacao, criado_em
FROM Pedido
WHERE validador_agente = 'ValidadorPedido'
ORDER BY criado_em DESC;
```

Result:

```
id | valor  | validador_agente | score_confianca | motivo_validacao       | criado_em
1  | 150.00 | ValidadorPedido  | 95              | Valor e moeda válidos  | 2025-01-11 10:30:00
2  | 250.00 | ValidadorPedido  | 88              | Valor e moeda válidos  | 2025-01-11 10:32:00
```

---

## Exemplo 4: Multi-Driver com Agentes (SQLite → PostgreSQL)

### Development (SQLite)

Seu agente valida em SQLite:

```yaml
# language_config.yaml
database:
  driver: "sqlite"
  dsn: "./dev.db"
```

**Código Corplang (idêntico):**

```mp
let pedido = criar_pedido_auditado(123, 150.00, "BRL")
let repo = new PedidoRepository()
repo.criar(pedido)
```

### Production (PostgreSQL)

Mude apenas a config:

```yaml
database:
  driver: "postgresql"
  dsn: "postgresql://user:pass@prod.db:5432/app"
```

**Mesmo código Corplang executa em PostgreSQL:**

```mp
# Nenhuma mudança no código!
let pedido = criar_pedido_auditado(123, 150.00, "BRL")
let repo = new PedidoRepository()
repo.criar(pedido)  # Agora usa PostgreSQL
```

**Migração automática:**

```bash
# Gera migrações com sintaxe PostgreSQL
mf db makemigrations

# Aplica ao PostgreSQL
mf db migrate
```

---

## Pattern: AgentPredictExecutor & Driver Abstraction

### Fluxo Interno

```
┌───────────────────────────────────┐
│ Corplang Code                     │
│ let usuario = criar_usuario(...)  │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│ AgentPredictExecutor              │
│ • Invoca agente                   │
│ • Coleta decisão + metadata       │
│ • Popula campos de auditoria      │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│ UsuarioRepository.criar()         │
│ (Driver abstrato)                 │
└────────┬────────────┬─────────────┘
         │            │
         ▼            ▼
    ┌─────────┐  ┌──────────────┐
    │ SQLite  │  │ PostgreSQL   │
    │ INSERT  │  │ INSERT       │
    └─────────┘  └──────────────┘
```

**Ponto-chave:** Lógica de validação de agente é independente do driver. Mesma validação trabalha em SQLite (dev) e PostgreSQL (prod).

---

## Exemplo 5: Tratamento de Conflitos em Migrations

### Cenário: Dois Agentes Gerando Schema Simultaneamente

**Timeline:**

```
10:30 → Agent A: "Deve adicionar campo `segmento`"
        mf db makemigrations
        ✓ Cria: migrations/002_add_segmento.json

10:31 → Agent B: "Deve adicionar campo `categoria`"
        mf db makemigrations
        ✓ Cria: migrations/003_add_categoria.json
```

**Aplicar em ordem:**

```bash
mf db migrate
```

Output:

```
✓ Applying 002_add_segmento.json
✓ Applying 003_add_categoria.json
✓ All migrations applied successfully
```

**Sem reordenação, sem conflito!**

---

## Exemplo 6: Validação em Nível de Constraint

### Natural Key Validation

Imagine um agente que valida que pares (usuario_id, empresa_id) são únicos:

```mp
model UsuarioEmpresa {
  usuario_id: int not_null
  empresa_id: int not_null
  role: text default "user"
  
  # Constraint de unicidade
  unique: [usuario_id, empresa_id]
}
```

**Agente que garante isso:**

```mp
agent ValidadorUnicidade {
  config: { "provider": "ollama", "model": "llama2" }
  
  fn existe_vinculo(usuario_id: int, empresa_id: int) -> bool {
    let repo = new UsuarioEmpresaRepository()
    let existente = repo.buscar(usuario_id, empresa_id)
    return existente != null
  }
}

fn criar_vinculo(usuario_id: int, empresa_id: int, role: text) -> bool {
  let validador = new ValidadorUnicidade()
  
  if validador.existe_vinculo(usuario_id, empresa_id) {
    println("✗ Vínculo já existe")
    return false
  }
  
  var vinculo = UsuarioEmpresa {
    usuario_id: usuario_id,
    empresa_id: empresa_id,
    role: role
  }
  
  let repo = new UsuarioEmpresaRepository()
  return repo.criar(vinculo)
}
```

---

## Checklist: Implementar Validação com IA

- [ ] Definir `model` com campos de auditoria (`validador_agente`, `score_confianca`, etc)
- [ ] Criar agente com lógica de validação
- [ ] Implementar pipeline (validar → enriquecer → salvar)
- [ ] Populár campos de auditoria antes de inserir
- [ ] Testar em SQLite (dev)
- [ ] Gerar migrations: `mf db makemigrations`
- [ ] Mudar para PostgreSQL (prod)
- [ ] Aplicar migrations: `mf db migrate`
- [ ] Verificar auditoria no banco: `SELECT * FROM <table> WHERE validador_agente = '<agent>'`

---

## Performance: Validação vs Latência

### Problema: Cada inserção é lenta?

Se seu agente leva 2 segundos por validação:

```
100 registros × 2s = 200 segundos!
```

### Solução: Batch Validation

```mp
fn criar_usuarios_em_lote(usuarios: [text]) -> [bool] {
  var resultados = []
  var validador = new ValidadorEmail()  # Instancia uma vez
  
  for (var email in usuarios) {
    let resultado = validador.validar(email)
    resultados.append(resultado.valido)
  }
  
  return resultados
}
```

O agente **mantém contexto** entre validações — segunda chamada é mais rápida.

---

## Próximas Leituras

1. **Migrations Detalhadas**: [MULTI_DRIVER_MIGRATIONS.md](MULTI_DRIVER_MIGRATIONS.md)
2. **Observabilidade**: [runtime_architecture.md](runtime_architecture.md#observabilitymanager)
3. **Implementar Novo Provider**: [guides/intelligence-providers.md](guides/intelligence-providers.md)

---

## Resumo

| Aspecto | Corplang | Traditional ORM |
|--------|----------|-----------------|
| Validação | Agente IA nativo | Função auxiliar |
| Decisão | Rastreável e auditável | Caixa preta |
| Schema Evolution | Dirigida por agente | Manual |
| Multi-driver | Mesmo código | Adapters |
| Auditoria | Integrada | Requer tabela extra |

Corplang faz da inteligência uma parte estrutural da camada de dados.
