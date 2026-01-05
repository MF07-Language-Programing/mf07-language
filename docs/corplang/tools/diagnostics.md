# Sistema de Diagnóstico de Exceções

O módulo **diagnostics** é responsável por formatar exceções e stack traces da linguagem Corplang de forma clara, amigável e profissional, semelhante ao que você vê em linguagens como Java, Python ou Rust.

## 🎯 O que ele resolve?

Quando algo dá errado no seu código `.mp`, em vez de ver um stack trace confuso de Python interno, você vê:

```
Error<ReferenceError>
Message: Variable 'usuario' not defined
Location: main.mp:15 in calcularTotal

StackTrace (.mp):
  at main.mp:15  in calcularTotal  <-- origem do erro
    codeblock: var total = usuario.saldo * 1.1
    variáveis: {saldo=100 (int); taxa=1.1 (float)}
  at main.mp:42  in processarVenda  
    codeblock: var valor = calcularTotal(cliente)
    variáveis: {cliente=Cliente#123 (Cliente); +2 more}

Root Cause:
  Possible error at main.mp:15
  Message: Variable 'usuario' not defined
  Note: undefined reference / missing symbol

Suggestions:
  - Ensure variable is defined before use; check variable name spelling and scope.
  - If referencing a module symbol, ensure the module is imported and the name exported.
```

## ✨ Características

- ✅ **Apenas frames `.mp`** — código Python interno fica oculto por padrão
- ✅ **Variáveis locais** mostradas automaticamente em cada frame
- ✅ **Código-fonte** da linha problemática incluído
- ✅ **Sugestões contextuais** baseadas no tipo de erro
- ✅ **Mensagens limpas** — sem aspas duplicadas ou newlines no meio

## 📖 Como usar no seu código Corplang

### Lançar exceção customizada

```corplang
fn validarIdade(idade: int) {
    if idade < 18 {
        raise new ValidationError("Idade mínima: 18 anos")
    }
}
```

### Capturar e imprimir stack trace

```corplang
try {
    validarIdade(15)
} catch (erro) {
    erro.printStackTrace()  # Imprime stack trace formatado
}
```

### Obter diagnóstico interno

```corplang
try {
    funcaoQueQuebra()
} catch (erro) {
    erro.printInternalDiagnostics()  # Mostra trace Python completo (debug)
}
```

## 🔧 API Python para integração

### Classificar exceção

```python
from src.corplang.tools.diagnostics import classify_exception

try:
    # código que pode quebrar
except Exception as exc:
    tipo = classify_exception(exc)
    print(f"Tipo de erro: {tipo}")
    # Saída: "ReferenceError", "IOError", "TimeoutError", etc.
```

### Formatar exceção completa

```python
from src.corplang.tools.diagnostics import format_exception

try:
    # executar código .mp
except Exception as exc:
    texto_formatado = format_exception(
        exc,
        executor=executor_instance,
        interpreter=interpreter_instance,
        workspace_root="/path/to/project"
    )
    print(texto_formatado)
```

### Criar exceção no estilo .mp

```python
from src.corplang.tools.diagnostics import wrap_as_mp_exception

try:
    # código que falha
except Exception as exc:
    mp_exception = wrap_as_mp_exception(
        exc,
        executor=executor,
        interpreter=interpreter,
        workspace_root=project_root
    )
    
    # Agora mp_exception tem:
    print(mp_exception.type)               # Tipo categoric
o
    print(mp_exception.message)            # Mensagem limpa
    print(mp_exception.mpStack)            # Stack congelado
    mp_exception.printStackTrace()         # Imprime formatado
```

## 🔍 Tipos de erro classificados

O sistema mapeia automaticamente exceções para categorias:

| Exceção Python         | Categoria Corplang    | Descrição                    |
|------------------------|----------------------|------------------------------|
| `FileNotFoundError`    | `FileNotFoundError`  | Arquivo não encontrado       |
| `OSError`, `IOError`   | `IOError`            | Erro de I/O                  |
| `asyncio.TimeoutError` | `TimeoutError`       | Operação demorou demais      |
| `asyncio.CancelledError` | `ConcurrencyError` | Tarefa async cancelada       |
| `MemoryError`          | `MemoryError`        | Sem memória                  |
| `AssertionError`       | `AssertionError`     | Asserção falhou              |
| Interno ExecutionError | `ReferenceError`     | Variável não definida        |
| Interno ExecutionError | `TypeError`          | Tipos incompatíveis          |

## 🧰 Funções auxiliares

### Mensagem segura

```python
from src.corplang.tools.diagnostics import safe_message

# Extrai mensagem de qualquer objeto sem explodir
mensagem = safe_message(exception_obj)
```

Útil quando você não tem certeza se o objeto tem `.message`, `.__str__()`, ou nada.

## 💡 Exemplo completo de uso

```python
from src.corplang.executor import execute
from src.corplang.tools.diagnostics import format_exception, wrap_as_mp_exception

def executar_codigo_seguro(codigo_mp: str):
    try:
        ast = parse_file(codigo_mp)
        execute(ast)
    except Exception as exc:
        # Formatar para exibir ao usuário
        trace_formatado = format_exception(
            exc,
            workspace_root="/home/projeto"
        )
        print(trace_formatado)
        
        # Ou empacotar como exceção .mp para propagação
        mp_exc = wrap_as_mp_exception(exc)
        return {"error": True, "exception": mp_exc}
    
    return {"error": False}
```

## 🎨 Personalizando diagnóstico

### Mostrar trace Python interno

Por padrão, o trace interno de Python fica oculto. Para debug profundo:

```python
# No interpreter, ative o flag:
interpreter.show_internal_diagnostics = True

# Agora format_exception incluirá seção "Internal Interpreter Diagnostics"
```

### Ajustar resumo de variáveis

Internamente, o sistema mostra até 3 variáveis por frame. Para ajustar:

```python
# Isso é configurado via função interna _summarize_variables
# Você pode reimplementar ou estender conforme necessário
```

## 📊 Estrutura de dados

### FrameInfo

Cada frame no stack trace tem esta estrutura:

```python
@dataclass
class FrameInfo:
    file_path: str              # Caminho absoluto do arquivo
    rel_path: str               # Caminho relativo ao workspace
    line: Optional[int]         # Número da linha
    column: Optional[int]       # Coluna (se disponível)
    function: Optional[str]     # Nome da função
    node: Optional[str]         # Tipo do nó AST
    code: Optional[str]         # Linha de código-fonte
    variables: Dict[str, Any]   # Variáveis locais
    memory_estimate: Optional[int]  # Estimativa de memória usada
```

## 🚀 Performance

O sistema é otimizado para:
- **Falhas raras**: Exceções são situações anormais, então não precisa ser ultra-rápido
- **Mensagens limpas**: Remove newlines, trunca strings longas, evita repr() explosivos
- **Apenas .mp frames**: Ignora milhares de frames Python internos

## 🔒 Segurança

- ✅ **Nunca falha ao formatar**: Todos os try/except internos garantem que você sempre recebe alguma mensagem
- ✅ **Safe repr**: Mesmo objetos com `__repr__` quebrado são handled gracefully
- ✅ **Sem vazamento de memória**: Referências circulares são evitadas

---

**Dica profissional**: Use `safe_message()` sempre que precisar extrair texto de qualquer objeto desconhecido. É a função mais robusta do módulo e nunca falha.
