# 🚀 Corplang CLI - Quick Start Guide

## Instalação

```bash
# Nenhuma instalação necessária! Use diretamente:
python -m src.commands --help
```

## Primeiros Passos

### 1. Criar um novo projeto
```bash
python -m src.commands init meu_projeto
cd meu_projeto
```

### 2. Editar o programa
```bash
# Edite main.mp conforme necessário
```

### 3. Executar
```bash
python -m src.commands run main.mp
```

## Comandos Principais

| Comando | Descrição |
|---------|-----------|
| `run` | Executar programa .mp |
| `compile` | Compilar para AST |
| `init` | Criar novo projeto |
| `version` | Ver versão |
| `versions` | Gerenciar versões |
| `env` | Validar ambiente |
| `build` | Construir pacotes |
| `db` | Operações de DB |
| `docs` | Gerar documentação |

## Exemplos Práticos

### Compilar um arquivo
```bash
python -m src.commands compile main.mp
```

### Compilar um diretório inteiro
```bash
python -m src.commands compile --dir ./src
```

### Validar ambiente
```bash
python -m src.commands env validate
```

### Sincronizar configurações
```bash
python -m src.commands env config sync
```

### Gerar documentação
```bash
python -m src.commands docs . --output ./docs
```

### Listar versões
```bash
python -m src.commands versions list --detailed
```

## Configuração

Dois arquivos de configuração:

**eco.system.json** - Estrutura do projeto
```json
{
  "corplang": {
    "version": "0.1.0",
    "environment": "development"
  }
}
```

**language_config.yaml** - Configuração da linguagem
```yaml
corplang:
  version: "0.1.0"
  name: "meu-projeto"
```

## Troubleshooting

### Erro: "Module not found"
```bash
# Sincronize as configurações
python -m src.commands env config sync
python -m src.commands env validate
```

### Erro: "Path not found"
```bash
# Use paths relativos ao projeto ou absolutos
python -m src.commands run ./main.mp
python -m src.commands run $(pwd)/main.mp
```

### Erro de compilação
```bash
# Use verbose para mais detalhes
python -m src.commands compile main.mp --verbose
```

## Estrutura do Projeto

Criado por `mf init`:
```
meu_projeto/
├── main.mp                      # Arquivo principal
├── language_config.yaml         # Config da linguagem
├── eco.system.json              # Config do ecossistema
├── README.md                    # Documentação
├── .gitignore                   # Git ignore
├── lib/                         # Bibliotecas locais
├── src/                         # Código-fonte
└── modules/                     # Módulos customizados
```

## Variáveis de Ambiente

```bash
# Ativar debug
export CORPLANG_DEBUG=1

# Forçar verificação de tipos
export CORPLANG_STRICT=1

# Definir diretório home
export CORPLANG_HOME=/custom/path

# Definir versão ativa
export CORPLANG_ACTIVE_VERSION=0.2.0
```

## Dicas Profissionais

1. **Sempre sincronize antes de trabalhar**
   ```bash
   python -m src.commands env config sync
   ```

2. **Compile frequentemente**
   ```bash
   python -m src.commands compile --dir ./src --verbose
   ```

3. **Validate seu ambiente**
   ```bash
   python -m src.commands env validate
   ```

4. **Gere documentação**
   ```bash
   python -m src.commands docs . --output ./docs
   ```

5. **Teste antes de commitar**
   ```bash
   python scripts/test_cli.py
   ```

## Suporte

Para mais informações, veja [README.md](./README.md)

---

**Status:** ✅ Pronto para produção
**Versão:** 0.1.0
**Data:** 2026-01-01
