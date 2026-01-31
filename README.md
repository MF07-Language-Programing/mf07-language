# Corplang — A Linguagem Nativa de Inteligência Autônoma

**A inteligência não é um plugin. É o core.**

Corplang é uma linguagem de programação que coloca **agentes de IA como primitivas de primeira classe**. Ao invés de integrar IA como uma biblioteca ou middleware, ela é tecida no tecido da execução — capacitando código a tomar decisões autônomas, validar dados através de raciocínio, e orquestrar múltiplos agentes em pipelines de dados e processos.

Construída sobre uma arquitetura de runtime profissional com:
- **Sistema de Versões Robusto**: Implantação segura e auditável de múltiplas versões
- **Multi-Driver Persistence**: SQLite, PostgreSQL, e extensível para qualquer backend
- **Agentes Orquestrados**: Roteamento nativo de múltiplos agentes com estado persistente
- **Type Safety em Runtime**: Validação de contratos genéricos sem sacrificar flexibilidade
- **Observabilidade Integrada**: Rastreamento de execução de nós e análise de performance

---

## Comece em 2 Minutos

### Instalação Rápida

### Linux / macOS
```bash
curl -fsSL https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
iwr -useb https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/install.sh | iex
```

### Windows (Git Bash)
```bash
curl -fsSL https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/install.sh | bash
```

### Instalação Manual
```bash
# Via Python
python -m src.commands --help

# Via script wrapper (Unix/Linux)
chmod +x mf
./mf --help

# Via batch script (Windows)
mf.bat --help
```

## Seu Primeiro Agente (5 min)

A forma mais rápida de entender Corplang é criar um **agente autônomo**:

```bash
mf init meu_assistente
cd meu_assistente
```

Crie `main.mp`:

```mp
agent Assistente {
  config: {
    "provider": "local",      # Usa LLM local (Ollama) ou remoto (OpenAI)
    "model": "llama2",
    "temperature": 0.7
  }
  
  fn processar(comando: text) -> text {
    # O agente não apenas executa — ele "pensa"
    let resposta = invoke self with comando
    return resposta
  }
}

fn main() {
  let assistente = new Assistente()
  
  # Agentes mantêm contexto entre chamadas
  println(assistente.processar("Qual é a data de hoje?"))
  println(assistente.processar("E o dia da semana?"))  # Agente lembra do contexto
  
  # Multi-Agent Routing nativo
  let resultado = route [assistente] with "Resuma em uma linha"
  println(resultado)
}
```

Execute com:

```bash
mf run main.mp
```

Para tutoriais completos, veja [Guia de Tutoriais](docs/tutorials/INDEX.md).

## Comandos Disponíveis

### `mf run <file.mp>`
Executa um programa Corplang.

```bash
mf run main.mp
mf run examples/first_project/main.mp
mf run programa.mp --verbose
mf run --strict tipos_exatos.mp
```

### `mf compile [file.mp|--dir <path>]`
Compila programa(s) Corplang.

```bash
# Compilar arquivo único
mf compile main.mp
mf compile main.mp -o compiled.pickle

# Compilar diretório
mf compile --dir ./src
mf compile --dir ./src --no-recursive
```

### `mf init [project-name] [--dir <path>]`
Cria novo projeto Corplang.

```bash
mf init meu_projeto
mf init meu_projeto --dir /caminho/customizado
```

Estrutura criada:
```
meu_projeto/
├── main.mp
├── language_config.yaml
├── README.md
├── .gitignore
├── lib/
├── src/
└── modules/
```

### `mf version [--verbose]`
Mostra versão do Corplang.

```bash
mf version
mf version --verbose
```

### `mf versions <command>`
Gerencia versões instaladas.

#### `mf versions list [--detailed]`
Lista versões instaladas.

```bash
mf versions list
mf versions list --detailed
```

#### `mf versions set <version>`
Define versão ativa.

```bash
mf versions set 0.2.0
mf versions set local
```

Nota sobre ativação imediata:

- Linux/macOS: o CLI aplica a versão no shell atual automaticamente. Em ambientes com políticas de segurança que bloqueiem injeção no TTY, o CLI mostrará um único comando `eval` de fallback.
- Windows (PowerShell): a versão é carregada automaticamente ao retorno do prompt via perfil do PowerShell (sem passos manuais). Sessões novas também herdam a configuração.
- Windows (cmd.exe): recomenda-se usar PowerShell para ativação imediata; novas sessões de cmd herdam a configuração persistida.

#### `mf versions install <version> [--from-url <URL>] [--force]`
Instala nova versão.

```bash
mf versions install 0.2.0
mf versions install 0.2.0 --force
```

#### `mf versions repair <version>`
Repara versão corrompida.

```bash
mf versions repair 0.1.0
```

### `mf env <command>`
Gerencia ambiente de execução.

#### `mf env validate`
Valida configuração do ambiente.

```bash
mf env validate
```

#### `mf env config <action>`
Gerencia arquivos de configuração.

```bash
mf env config validate
mf env config sync
mf env config show
```

### `mf build [wheel|exe]`
Constrói pacotes e executáveis.

```bash
mf build
mf build wheel
mf build exe
```

### `mf db <command>`
Operações com banco de dados (suporta SQLite, PostgreSQL e mais).

#### `mf db init [path]`
Inicializa estrutura de migrações.

```bash
mf db init
mf db init ./custom_migrations
```

#### `mf db connect <driver> <dsn>`
Testa conexão com banco.

```bash
mf db connect sqlite test.db
mf db connect postgresql postgres://user@localhost/db
```

#### `mf db makemigrations`
Detecta mudanças nos modelos e gera plano de migração.

```bash
mf db makemigrations
# Cria: migrations/plan.initial.json (primeira vez)
#       migrations/plan.incremental.json (atualizações)
```

#### `mf db migrate`
Aplica migrações ao banco de dados.

```bash
mf db migrate
# Aplica plano de migração ao banco configurado em language_config.yaml
```

**Drivers Suportados:**
- `sqlite` - Desenvolvimento e testes (arquivo local)
- `postgresql`/`postgres` - Produção (alta performance)
- Extensível para MySQL, SQL Server, etc.

Veja [MULTI_DRIVER_MIGRATIONS.md](docs/MULTI_DRIVER_MIGRATIONS.md) para detalhes.

### `mf docs <path> [--output <dir>] [--format <type>]`
Gera documentação do projeto.

```bash
mf docs .
mf docs ./my_project --output ./documentation
mf docs . --format markdown
```

## Configuração

### eco.system.json
Configuração de ambiente do projeto.

```json
{
  "corplang": {
    "version": "0.1.0",
    "environment": "development"
  }
}
```

### language_config.yaml
Configuração específica da linguagem.

```yaml
corplang:
  version: "0.1.0"
  name: "meu-projeto"
  
module_paths:
  - ./lib
  - ./src
  
compile:
  strict: false
  target: "3.9"
```

## Variáveis de Ambiente

| Variável | Descrição |
|----------|-----------|
| `CORPLANG_ACTIVE_VERSION` | Versão ativa para execução |
| `CORPLANG_DEBUG` | Ativa output de debug |
| `CORPLANG_STRICT` | Força verificação de tipos |
| `CORPLANG_HOME` | Diretório home personalizado |

```bash
export CORPLANG_ACTIVE_VERSION=local
export CORPLANG_DEBUG=1
mf run programa.mp
```

## Resolução de Paths

O CLI suporta paths relativos:

```bash
# Relativo ao projeto
mf run ./src/main.mp

# Relativo à localização corrente
mf run ../sibling_project/main.mp

# Absoluto
mf run /home/user/corplang/program.mp
```

## Casos de Uso Comuns

### Novo Projeto
```bash
mf init hello-world
cd hello-world
mf run main.mp
```

### Compilar Tudo
```bash
mf compile --dir ./src
mf compile --dir ./lib
```

### Configurar Ambiente
```bash
mf env config sync
mf env validate
```

### Gerenciar Versões
```bash
mf versions list
mf versions set 0.2.0
```

### Desinstalar Corplang
```bash
# Remover completamente do sistema
mf uninstall

# Desinstalação não-interativa
mf uninstall --yes

# Via script standalone
curl -fsSL https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/uninstall.sh | bash
```

Para mais detalhes, consulte [docs/UNINSTALL_GUIDE.md](docs/UNINSTALL_GUIDE.md).

## Filosofia & Pilares

### Inteligência Autônoma como Primitiva
Em Corplang, agentes IA não são "features" — são **cidadãos de primeira classe**. Cada nó na AST é rastreável, cada agente mantém estado entre execuções, e o roteamento de múltiplos agentes é nativo ao runtime.

### Corpo Técnico, Mente Inteligente
A arquitetura separa dois mundos que normalmente colapsam:
- **Corpo**: Compilador, drivers de dados, CLI, sistema de versões (tudo determinístico e auditável)
- **Mente**: Agentes, providers de IA, raciocínio e tomada de decisão (tudo extensível e observável)

### Production-Grade desde o Dia Um
- **Versionamento auditável** de múltiplas versões simultâneas
- **Persistência agnóstica a driver**: SQLite para prototipagem, PostgreSQL para escala
- **Observabilidade integrada**: Rastreie cada decisão do agente

### Type Safety Pragmático
Validação de contratos genéricos em runtime — segurança onde importa, flexibilidade onde faz sentido.

---

## Troubleshooting

### "No versions installed"
```bash
mf versions list --detailed
# Usa versão local do repositório
```

### "Path not found"
```bash
# Use caminhos absolutos ou relativos ao projeto
mf run $(pwd)/main.mp
```

### "Configuration mismatch"
```bash
# Sincroniza configs
mf env config sync
# Valida
mf env validate
```

## Arquitetura Interna

O CLI é organizado em:

- **config.py** - Gerenciamento de configurações, versões
- **utils.py** - Utilidades comuns (output, validação, timers)
- **handlers/** - Implementação dos subcomandos
  - compile.py
  - run.py
  - init.py
  - versions.py
  - env.py
  - build.py
  - db.py
  - docs.py

## Contribuindo

Para adicionar novo subcomando:

1. Crie `handlers/novo_comando.py`
2. Implemente `handle_novo_comando(args) -> CLIResult`
3. Adicione parser em `create_novo_comando_parser()`
4. Adicione ao import e criação no `main.py`

## Licença

MIT - Veja LICENSE para detalhes.
