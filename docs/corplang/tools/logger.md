# Sistema de Logging Estruturado

O **logger** da Corplang oferece um sistema de logging profissional, estruturado e configurável, ideal para rastreamento de execução, debug e monitoramento de aplicações `.mp`.

## 🎯 Por que usar o logger?

Em vez de usar `print()` espalhados pelo código, o logger oferece:

- ✅ **Níveis de log** (DEBUG, INFO, WARN, ERROR, FATAL)
- ✅ **Logs estruturados** com campos nomeados
- ✅ **Colorização** automática no terminal
- ✅ **Filtros configuráveis** por módulo
- ✅ **Zero custo** quando desabilitado

## 📖 Uso básico no código Corplang

```corplang
import Logger from utils.logger

var logger = new Logger("MeuModulo")

logger.info("Aplicação iniciada")
logger.warn("Cache não encontrado, usando configuração padrão")
logger.error("Falha ao conectar ao banco de dados")
```

## 🔧 API Python para integração

### Obter logger

```python
from src.corplang.tools.logger import get_logger

logger = get_logger(__name__)
logger.info("Sistema iniciado")
```

### Logs com contexto

```python
logger.info(
    "Usuário autenticado",
    user_id=123,
    ip="192.168.1.1",
    timestamp="2026-01-01T10:00:00Z"
)
```

**Saída:**
```
INFO  | Usuário autenticado | user_id=123 ip=192.168.1.1 timestamp=2026-01-01T10:00:00Z
```

### Diferentes níveis

```python
logger.debug("Variável x tem valor 42")        # Apenas em modo debug
logger.info("Processamento concluído")         # Informação geral
logger.warn("Arquivo de config ausente")       # Aviso não-crítico
logger.error("Falha ao salvar dados")          # Erro recuperável
logger.fatal("Sistema corrompido, abortando") # Erro fatal
```

## ⚙️ Configuração via `config.yml`

```yaml
logging:
  level: "INFO"           # DEBUG, INFO, WARN, ERROR, FATAL
  format: "structured"    # structured, simple, json
  color: true            # Colorir output no terminal
  show_timestamp: true   # Incluir timestamp em cada log
  
  # Filtros por módulo
  filters:
    "corplang.compiler": "DEBUG"    # Mais verbose no compiler
    "corplang.executor": "INFO"     # Normal no executor
    "corplang.stdlib": "WARN"       # Apenas warnings na stdlib
```

## 🎨 Formatos de saída

### Structured (padrão)

```
INFO  | Módulo carregado | module=collections.list path=/stdlib/core/collections/list.mp
WARN  | Cache desabilitado | reason=arquivo_corrompido
ERROR | Import falhou | module=unknown.module
```

### Simple

```
[INFO] Módulo carregado
[WARN] Cache desabilitado
[ERROR] Import falhou
```

### JSON

```json
{"level": "INFO", "message": "Módulo carregado", "module": "collections.list", "path": "/stdlib/core/collections/list.mp"}
{"level": "WARN", "message": "Cache desabilitado", "reason": "arquivo_corrompido"}
{"level": "ERROR", "message": "Import falhou", "module": "unknown.module"}
```

## 🔍 Filtragem avançada

### Por nível

```python
# Mostrar apenas WARN e acima
logger.set_level("WARN")

logger.debug("Isso não aparece")
logger.info("Isso também não")
logger.warn("Isso aparece")       # ✓
logger.error("Isso também")       # ✓
```

### Por módulo

```python
from src.corplang.tools.logger import set_module_level

# Habilitar debug apenas no lexer
set_module_level("corplang.compiler.lexer", "DEBUG")

# Silenciar completamente um módulo barulhento
set_module_level("corplang.stdlib.http", "ERROR")
```

## 💡 Padrões recomendados

### Em desenvolvimento

```python
# Verbose para debug rápido
logger.set_level("DEBUG")
```

```corplang
# Em .mp, crie logger no topo do arquivo
var logger = new Logger("MeuApp")

intent processar(dados: list) {
    logger.debug("Iniciando processamento de {dados.size()} items")
    
    for item in dados {
        logger.debug("Processando item: {item}")
        # ...
    }
    
    logger.info("Processamento concluído com sucesso")
}
```

### Em produção

```python
# Apenas INFO e acima
logger.set_level("INFO")
```

```corplang
var logger = new Logger("ProdApp")

intent operacaoCritica() {
    logger.info("Iniciando operação crítica")
    
    try {
        # operação perigosa
        logger.info("Operação concluída")
    } catch (erro) {
        logger.error("Falha na operação: {erro.message}")
        raise erro
    }
}
```

## 🚨 Logging de exceções

```python
try:
    # código que pode falhar
except Exception as exc:
    logger.error(
        f"Falha inesperada: {exc}",
        exc_type=type(exc).__name__,
        exc_message=str(exc)
    )
```

## 📊 Métricas e observabilidade

### Contar eventos

```python
from src.corplang.tools.logger import get_logger

logger = get_logger(__name__)
contador = 0

for item in items:
    contador += 1
    if contador % 100 == 0:
        logger.info(f"Progresso: {contador} items processados")
```

### Medir tempo

```python
import time

logger.info("Iniciando operação lenta")
inicio = time.time()

# operação demorada

duracao = time.time() - inicio
logger.info(f"Operação concluída", duration_seconds=duracao)
```

## 🎭 Contexto dinâmico

```python
class ProcessadorPedidos:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def processar(self, pedido_id: int):
        # Adicionar contexto ao logger para todas as mensagens seguintes
        self.logger = self.logger.with_context(pedido_id=pedido_id)
        
        self.logger.info("Iniciando processamento")
        self.logger.info("Validando dados")        # Ambos incluem pedido_id
        self.logger.info("Salvando no banco")      # automaticamente
```

## 🔒 Segurança

**Cuidado**: Nunca logue informações sensíveis:

```python
# ❌ MAU
logger.info(f"Login: {usuario.senha}")

# ✅ BOM
logger.info("Login bem-sucedido", user_id=usuario.id)
```

## 🚀 Performance

O logger é otimizado para **zero overhead** quando desabilitado:

```python
if logger.is_enabled_for("DEBUG"):
    # Operação cara para gerar mensagem de debug
    mensagem_complexa = gerar_relatorio_detalhado()
    logger.debug(mensagem_complexa)
```

## 📦 Integração com outras ferramentas

### Com diagnostics

```python
from src.corplang.tools.diagnostics import safe_message
from src.corplang.tools.logger import get_logger

logger = get_logger(__name__)

try:
    # código
except Exception as exc:
    logger.error(f"Erro: {safe_message(exc)}")
```

### Com UI de terminal

```python
from src.corplang.core.ui.terminal import ui
from src.corplang.tools.logger import get_logger

logger = get_logger(__name__)

ui.status("Compilando", "main.mp")
logger.info("Compilação iniciada", file="main.mp")

# ... compilação ...

ui.success("Compilação completa")
logger.info("Compilação bem-sucedida")
```

---

**Dica**: Em desenvolvimento, use `DEBUG`. Em produção, use `INFO` ou `WARN`. Logs são seus amigos para diagnosticar bugs em produção!
