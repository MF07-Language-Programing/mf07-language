# Corplang CLI - Command Reference

A modern, production-grade command-line interface para a linguagem Corplang.

## Instalação Rápida

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
Operações com banco de dados.

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
