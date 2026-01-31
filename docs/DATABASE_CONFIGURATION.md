# Database Configuration Centralization

## Overview

A partir desta versão, toda configuração de banco de dados foi centralizada em um único arquivo `language_config.yaml` ao invés de espalhado entre múltiplos arquivos JSON/YAML.

## Configuração

No arquivo `language_config.yaml` do seu projeto, adicione a seção `database`:

```yaml
database:
  driver: "sqlite"    # ou "postgresql"
  dsn: "./app.db"     # caminho do arquivo (SQLite) ou connection string (PostgreSQL)
```

### Exemplos

**SQLite:**
```yaml
database:
  driver: "sqlite"
  dsn: "./myapp.db"
```

**PostgreSQL:**
```yaml
database:
  driver: "postgresql"
  dsn: "postgresql://user:password@localhost:5432/mydb"
```

**Em Memória (SQLite):**
```yaml
database:
  driver: "sqlite"
  dsn: ":memory:"
```

## Uso no Código

### Auto-conexão (Recomendado)

Quando você faz `import db`, a conexão é **automaticamente** estabelecida usando a configuração do arquivo `language_config.yaml`:

```mp
from models import User
import db

// Conexão já está pronta! Não precisa chamar db.connect()
var users = User.objects.all()
```

### Conexão Manual (Opcional)

Se preferir, pode ignorar a configuração e conectar manualmente:

```mp
from models import User
import db

db.connect("sqlite://./custom.db")

User.create(name="John", email="john@example.com")
```

## Migrações

As migrações usam automaticamente o banco de dados configurado em `language_config.yaml`:

```bash
# Gera plano de migrações baseado nos modelos
mf db makemigrations

# Aplica migrações usando o banco configurado
mf db migrate
```

Não é mais necessário manter `migrations/config.yaml` sincronizado.

## Mudanças Quebradoras

- ❌ O arquivo `migrations/config.yaml` deixou de ser usado
- ❌ Chamadas explícitas `db.connect()` ainda funcionam, mas agora é opcional
- ✅ Todos os projetos novos vêm com `language_config.yaml` pronto

## Migração de Projetos Existentes

Se você tem um projeto antigo, atualize o `language_config.yaml`:

1. Verifique qual banco está usando em `migrations/config.yaml` ou no código
2. Adicione a seção `database` no `language_config.yaml`
3. Remova as chamadas `db.connect()` do seu código (opcional)
4. Execute `mf db migrate` para aplicar migrações

## Estrutura Completa do language_config.yaml

```yaml
# Corplang Project Configuration

name: "meu_projeto"
description: "Descrição do projeto"
language_version: "0.1.0"

module_paths:
  - ./lib
  - ./src
  - ./modules

# ✨ NOVO: Configuração centralizada de banco de dados
database:
  driver: "sqlite"
  dsn: "./app.db"

compile:
  strict: false
  target: "3.9"
  optimize: false
  native_inline: true

runtime:
  max_recursion: 10000
  async_enabled: true
  memory_limit: 0

dev:
  debug: false
  ui_enabled: true
```

## Drivers Suportados

| Driver | Status | Exemplo |
|--------|--------|---------|
| SQLite | ✅ Completo | `./app.db` ou `:memory:` |
| PostgreSQL | ✅ Com `import db` | `postgresql://user:pass@host:5432/db` |

Mais drivers podem ser adicionados facilmente.
