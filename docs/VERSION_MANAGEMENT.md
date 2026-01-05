# Version Management System

Sistema avançado de gestão de versões do Corplang com integração GitHub e interface interativa.

## Arquitetura

### Componentes Principais

1. **VersionManager** (`src/commands/config.py`)
   - Gerencia versões instaladas localmente
   - Busca releases no GitHub via API
   - Download e instalação de versões remotas
   - Validação de integridade
   - Sistema de logs

2. **Interactive UI** (`src/commands/utils.py`)
   - `Spinner`: Animações para operações longas
   - `SelectMenu`: Menus interativos de seleção
   - `ProgressBar`: Barras de progresso para downloads

3. **Versions Handler** (`src/commands/handlers/versions.py`)
   - Lista versões instaladas e remotas
   - Instalação interativa com menu
   - Reparo de versões corrompidas
   - Visualização de logs

## Funcionalidades

### 1. Listar Versões

```bash
# Versões instaladas localmente
mf versions list

# Com detalhes
mf versions list --detailed

# Incluir versões disponíveis online
mf versions list --online

# Ambos
mf versions list --detailed --online
```

**Saída:**
```
─ Installed Versions ───────────────────────────────────
  ✓ local (active)
     Path:     /home/user/mf07-language
     Type:     development
     Installed: 2025-01-19T10:30:00

  ✓ v1.0.0
     Path:     /home/user/.corplang/versions/v1.0.0
     Type:     installed
     Installed: 2025-01-18T15:20:00

─ Available Online ─────────────────────────────────────
  1. v1.2.0
     Released: 2025-01-19T08:00:00

  2. v1.1.0 (pre-release)
     Released: 2025-01-15T12:00:00
```

### 2. Instalar Versões

#### Modo Interativo (padrão)
```bash
mf versions install
```

**Comportamento:**
1. Busca releases no GitHub
2. Exibe menu de seleção
3. Usuário escolhe com números 1-9 ou navegação j/k
4. Download com spinner animado
5. Instalação automática

#### Modo Direto
```bash
# Instalar versão específica
mf versions install v1.2.0

# De URL customizada
mf versions install v1.2.0 --from-url https://example.com/release.tar.gz

# Forçar reinstalação
mf versions install v1.0.0 --force
```

### 3. Definir Versão Ativa

```bash
mf versions set v1.0.0
```

Atualiza:
- Variável de ambiente `CORPLANG_ACTIVE_VERSION`
- `language_config.yaml` do projeto (se existir)

### 4. Reparar Versões

```bash
# Interativo (menu de versões)
mf versions repair

# Direto
mf versions repair v1.0.0
```

Verifica arquivos críticos:
- `src/corplang/compiler/lexer.py`
- `src/corplang/compiler/parser.py`
- `src/corplang/executor/__init__.py`

Se houver arquivos faltando, re-baixa a versão completa.

### 5. Logs de Operações

```bash
# Últimas 20 linhas
mf versions logs

# Últimas 50 linhas
mf versions logs --lines 50

# Logs de uma versão específica
mf versions logs v1.0.0
```

**Formato:**
```
2025-01-19T10:30:00 | INSTALL        | SUCCESS    | /home/user/.corplang/versions/v1.0.0
2025-01-19T10:32:15 | SET_ACTIVE     | SUCCESS    | v1.0.0
2025-01-19T11:05:22 | REPAIR         | VALID      | no issues found
```

## API do GitHub

### Configuração

**Token de autenticação** (opcional, aumenta rate limit):
```bash
export GITHUB_TOKEN=ghp_your_token_here
# ou
export GH_TOKEN=ghp_your_token_here
```

### Endpoints Utilizados

- **List Releases**: `GET /repos/MF07-Language-Programing/mf07-core-compiler/releases`
- **Rate Limit**: 60 req/hora (sem token), 5000 req/hora (com token)

### Estrutura de Release

```json
{
  "tag_name": "v1.2.0",
  "name": "Version 1.2.0",
  "published_at": "2025-01-19T08:00:00Z",
  "draft": false,
  "prerelease": false,
  "html_url": "https://github.com/repo/releases/tag/v1.2.0"
}
```

## Sistema de Logs

### Localização
`~/.corplang/version_manager.log`

### Formato
```
<timestamp> | <action> | <version> | <status> | <details>
```

### Ações Registradas
- `DOWNLOAD`: Download de versão
- `INSTALL`: Instalação completa
- `SET_ACTIVE`: Mudança de versão ativa
- `REPAIR`: Reparo/validação
- `ERROR`: Erros gerais

### Status Possíveis
- `STARTED`: Operação iniciada
- `SUCCESS`: Sucesso
- `FAILED`: Falha
- `ERROR`: Erro inesperado
- `VALID`: Validação bem-sucedida
- `REPAIRED`: Reparo concluído

## Interface Interativa

### Spinner

Animação durante operações longas:
```
⠹ Installing version v1.2.0...
```

Frames: `⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏`

### SelectMenu

Menu de seleção interativo:
```
Select version to install:
  1. v1.2.0
→ 2. v1.1.0
  3. v1.0.0
```

**Controles:**
- `1-9`: Seleção direta por número
- `j` ou `↓`: Próxima opção
- `k` ou `↑`: Opção anterior
- `Enter`: Confirmar seleção
- `q` ou `Esc`: Cancelar

### ProgressBar

```
Downloading █████████████████░░░░░░░░░░░░░ 65%
```

## Estrutura de Diretórios

```
~/.corplang/
├── versions/
│   ├── v1.0.0/
│   │   └── src/corplang/...
│   ├── v1.1.0/
│   │   └── src/corplang/...
│   └── v1.2.0/
│       └── src/corplang/...
└── version_manager.log
```

## Validação de Integridade

Arquivos obrigatórios para versão válida:
```
src/corplang/compiler/lexer.py
src/corplang/compiler/parser.py
src/corplang/executor/__init__.py
```

Se algum estiver faltando:
- Status: `✗ invalid`
- Comando `repair` pode corrigir

## Fallbacks e Degradação

### Modo Não-Interativo

Se `stdout` não for TTY:
- Menus exibidos como listas numeradas
- Auto-seleção da primeira opção
- Spinner substituído por mensagens simples

### GitHub Indisponível

- `fetch_remote_releases()` retorna lista vazia
- `install` requer `--from-url`
- Versões locais continuam funcionando

### Sem Versões Instaladas

- `versions list` retorna erro com exit code 1
- `versions install` funciona normalmente
- `versions set` não tem opções válidas

## Exemplo de Fluxo Completo

```bash
# 1. Listar versões disponíveis
$ mf versions list --online

─ Installed Versions ───────────────────────────────────
  ✓ local (active)

─ Available Online ─────────────────────────────────────
  1. v1.2.0
  2. v1.1.0
  3. v1.0.0

# 2. Instalar versão (interativo)
$ mf versions install

Select version to install:
→ 1. v1.2.0
  2. v1.1.0
  3. v1.0.0

✓ Installing version v1.2.0...
✓ Version v1.2.0 installed to /home/user/.corplang/versions/v1.2.0

# 3. Ativar versão
$ mf versions set v1.2.0
✓ Active version set to v1.2.0

# 4. Verificar status
$ mf versions list

─ Installed Versions ───────────────────────────────────
  ✓ local
  ✓ v1.2.0 (active)

# 5. Visualizar logs
$ mf versions logs

2025-01-19T11:10:05 | DOWNLOAD       | STARTED    | https://github.com/...
2025-01-19T11:10:42 | DOWNLOAD       | SUCCESS    | /home/user/.corplang/versions/v1.2.0
2025-01-19T11:10:42 | INSTALL        | SUCCESS    | /home/user/.corplang/versions/v1.2.0
2025-01-19T11:11:03 | SET_ACTIVE     | SUCCESS    | v1.2.0
```

## Integração com Projetos

### language_config.yaml

```yaml
corplang:
  version: v1.2.0
  strict: true

project:
  name: myproject
  description: "My Corplang project"
```

Comando `versions set` atualiza automaticamente este arquivo.

### Variável de Ambiente

```bash
export CORPLANG_ACTIVE_VERSION=v1.2.0
```

Sobrescreve configuração do `language_config.yaml`.

## Comparação com Old CLI

### Old CLI
- Função `list_online_releases(repo, per_page)` dispersa
- Instalação manual com muitos passos
- Logs básicos sem estrutura
- Sem interface interativa

### New CLI
- VersionManager orientado a objetos
- Instalação one-click com menus interativos
- Logs estruturados com filtros
- Animações e feedback visual
- Comandos modulares e testáveis

## Troubleshooting

### Erro: "Could not fetch releases from GitHub"
- Verifique conectividade
- Configure `GITHUB_TOKEN` se rate limit excedido
- Use `--from-url` para instalação alternativa

### Erro: "Version already installed"
- Use `--force` para reinstalar

### Versão Inválida
- Execute `mf versions repair <version>`
- Se não funcionar, desinstale manualmente: `rm -rf ~/.corplang/versions/<version>`

### Spinner Não Funciona
- Normal em ambientes sem TTY (CI/CD, scripts)
- Mensagens simples são exibidas automaticamente

## Próximas Melhorias

- [ ] Checksums SHA256 para verificação de integridade
- [ ] Cache local de releases para reduzir chamadas GitHub
- [ ] Instalação paralela de múltiplas versões
- [ ] Auto-update do CLI via versions
- [ ] Rollback automático em caso de falha
- [ ] Compression support (tar.gz, zip)
