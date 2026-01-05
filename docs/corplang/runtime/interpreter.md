# Módulo Executor - Interpretador Corplang

O **Executor** (também chamado de **Interpreter**) é o coração da execução de código Corplang. Ele percorre a AST (Árvore de Sintaxe Abstrata) gerada pelo parser e executa cada nó, transformando sua estrutura declarativa em ações reais.

## 🎯 O que ele faz?

Imagineque você escreveu este código `.mp`:

```corplang
var nome = "Corplang"
var idade = 5

intent saudar(pessoa: string) {
    print("Olá, {pessoa}!")
}

saudar(nome)
```

O **Parser** transformou isso em uma AST. Agora o **Executor**:
1. Cria uma variável `nome` com valor `"Corplang"`
2. Cria uma variável `idade` com valor `5`
3. Registra a função `saudar` no escopo global
4. Chama `saudar("Corplang")`
5. Dentro de `saudar`, executa `print("Olá, Corplang!")`

## 🏗️ Arquitetura

O executor usa um padrão **Registry de Executores**:

```
Interpreter
  ├── ExecutorRegistry (despacho de nós)
  │   ├── LiteralExecutor
  │   ├── IdentifierExecutor
  │   ├── BinaryOperatorExecutor
  │   ├── FunctionCallExecutor
  │   ├── IfExecutor
  │   ├── WhileExecutor
  │   └── ... (30+ executores especializados)
  │
  └── ExecutionContext (estado e escopo)
      ├── Environment (variáveis e funções)
      └── Call Stack (rastreamento)
```

Cada **tipo de nó** AST tem um **executor especializado** que sabe como executá-lo.

## 📖 Uso básico

### Executar um arquivo .mp

```python
from src.corplang.executor import execute, parse_file

# Parse + Execução
ast = parse_file("meu_programa.mp")
resultado = execute(ast)
```

### Executar código inline

```python
from src.corplang.compiler import Lexer
from src.corplang.compiler.parser import Parser
from src.corplang.executor import execute

codigo = '''
var x = 10
var y = 20
print(x + y)
'''

lexer = Lexer(codigo)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

execute(ast)  # Imprime: 30
```

## 🔧 API de Execução

### Interpreter Core

```python
from src.corplang.executor.interpreter import Interpreter
from src.corplang.executor.context import ExecutionContext

# Criar interpreter
interpreter = Interpreter()

# Criar contexto de execução
context = ExecutionContext(interpreter, current_file="main.mp")

# Executar um nó AST específico
resultado = interpreter.execute(node, context)
```

### Registrar executor customizado

```python
from src.corplang.executor.node import NodeExecutor
from src.corplang.executor.interpreter import ExecutorRegistry

class MeuExecutorCustomizado(NodeExecutor):
    def can_execute(self, node) -> bool:
        return type(node).__name__ == "MeuNovoTipoDeNo"
    
    def execute(self, node, context):
        # Lógica de execução
        return "resultado"

# Registrar no registry
registry = ExecutorRegistry()
registry.register(MeuExecutorCustomizado())
```

## 🧩 Executores Principais

### Expressões (`expressions.py`)

```python
# Literais
42          # LiteralExecutor
"texto"     # LiteralExecutor
true        # LiteralExecutor

# Operações binárias
x + y       # BinaryOperatorExecutor
a == b      # BinaryOperatorExecutor
lista[0]    # IndexAccessExecutor

# Chamadas
funcao()    # FunctionCallExecutor
obj.metodo() # PropertyAccessExecutor + FunctionCallExecutor
```

### Controle de Fluxo (`control_flow.py`)

```python
# If/Else
if condicao {
    # IfExecutor
}

# While
while x < 10 {
    # WhileExecutor
}

# For
for item in lista {
    # ForExecutor
}

# Try/Catch
try {
    # TryExecutor
} catch (erro) {
    # CatchExecutor
}
```

### Funções (`functions.py`)

```python
# Declaração
intent minhaFuncao(a: int, b: int) {
    # FunctionDeclarationExecutor
}

# Chamada
minhaFuncao(10, 20)  # FunctionCallExecutor

# Async
async intent buscarDados() {
    # AsyncFunctionExecutor
}

await buscarDados()  # AwaitExecutor
```

### OOP (`oop.py`)

```python
# Declaração de classe
class Pessoa {
    # ClassDeclarationExecutor
}

# Instanciação
var p = new Pessoa()  # NewExpressionExecutor

# Acesso a propriedade
p.nome  # PropertyAccessExecutor

# Chamada de método
p.falar()  # PropertyAccessExecutor + FunctionCallExecutor

# this
this.atributo  # ThisExecutor

# super
super.metodo()  # SuperExecutor
```

## 🔍 ExecutionContext e Escopo

### Gerenciar variáveis

```python
context = ExecutionContext(interpreter)

# Definir variável
context.define_var("x", 42, "int")

# Obter variável
valor = context.get_var("x")  # 42

# Atualizar variável
context.set_var("x", 50)

# Verificar existência
if context.has_var("x"):
    print("Variável existe!")
```

### Escopo hierárquico

```corplang
var global_var = "global"

intent funcao() {
    var local_var = "local"
    print(global_var)  # ✓ Acessa escopo pai
    print(local_var)   # ✓ Acessa escopo local
}

print(global_var)  # ✓ Acessa escopo global
print(local_var)   # ❌ Erro: local_var não definido
```

Internamente:

```python
# Escopo global
context_global = ExecutionContext(interpreter)
context_global.define_var("global_var", "global")

# Escopo de função (filha do global)
context_funcao = context_global.create_child()
context_funcao.define_var("local_var", "local")

# Variável global acessível na função
context_funcao.get_var("global_var")  # "global" ✓

# Variável local NÃO acessível no global
context_global.get_var("local_var")  # Erro ❌
```

## 🚀 Async/Await

O executor suporta código assíncrono nativamente:

```corplang
async intent buscarUsuario(id: int) {
    var dados = await http.get("/users/{id}")
    return dados
}

# No código síncrono, aguarda automaticamente
var usuario = buscarUsuario(123)
print(usuario.nome)
```

Internamente:

```python
import asyncio

# Executor detecta funções async e usa asyncio
resultado = asyncio.run(interpreter.execute_async(node, context))
```

## 🛡️ Tratamento de erros

### Capturar e propagar

```corplang
try {
    var resultado = operacaoPerigosa()
} catch (erro) {
    print("Erro capturado: {erro.message}")
    erro.printStackTrace()
}
```

Internamente:

```python
from src.corplang.core.exceptions import CorpLangRuntimeError

try:
    resultado = context.interpreter.execute(perigoso_node, context)
except CorpLangRuntimeError as exc:
    # Exceção da linguagem .mp
    print(f"Erro: {exc.message}")
    print(f"Stack: {exc.mp_stack}")
```

### Exceções da linguagem

```python
from src.corplang.core.exceptions import (
    CorpLangRuntimeError,
    RuntimeErrorType,
    CorpLangRaisedException
)

# Lançar erro de tipo
raise CorpLangRuntimeError(
    "Tipo incompatível: esperado int, recebeu string",
    RuntimeErrorType.TYPE_ERROR
)

# Lançar exceção customizada do usuário
raise CorpLangRaisedException(custom_user_exception_object)
```

## 📊 Call Stack e rastreamento

O interpreter mantém um call stack para diagnóstico:

```python
# Adicionar frame ao stack
with context.frame(
    file="main.mp",
    line=15,
    function="calcular",
    node=function_node
):
    # Execução dentro do frame
    resultado = context.interpreter.execute(body, context)

# Stack é automaticamente atualizado e usado em exceções
```

## 💡 Boas práticas

### 1. Sempre use ExecutionContext

```python
# ❌ Não faça isso
interpreter.execute(node)  # Sem contexto

# ✓ Faça isso
context = ExecutionContext(interpreter, current_file="main.mp")
interpreter.execute(node, context)
```

### 2. Limpe recursos async

```python
import asyncio

# Certifique-se de fechar o loop
try:
    asyncio.run(execute_async(ast))
finally:
    # Cleanup se necessário
    pass
```

### 3. Trate exceções adequadamente

```python
from src.corplang.tools.diagnostics import format_exception

try:
    execute(ast)
except Exception as exc:
    # Formatar para o usuário
    print(format_exception(exc, workspace_root="/projeto"))
```

## 🔧 Extensibilidade

### Adicionar builtin customizada

```python
from src.corplang.executor.builtins import register_builtin

def minha_funcao_nativa(arg1, arg2):
    return arg1 + arg2

# Registrar para ser chamável de .mp
register_builtin("minha_funcao", minha_funcao_nativa)
```

Agora em `.mp`:

```corplang
var resultado = minha_funcao(10, 20)
print(resultado)  # 30
```

## 📦 Objetos da linguagem

### CorpLangFunction

Representa uma função declarada em `.mp`:

```python
from src.corplang.executor.objects import CorpLangFunction

funcao = CorpLangFunction(
    node=function_node,
    closure_env=context.environment,
    interpreter=interpreter
)

# Chamar
resultado = funcao.call([arg1, arg2], context)
```

### ClassObject e InstanceObject

```python
from src.corplang.executor.objects import ClassObject, InstanceObject

# Classe
classe = ClassObject(
    name="Pessoa",
    methods={"falar": funcao_falar},
    properties={"nome": None, "idade": None}
)

# Instância
instancia = InstanceObject(classe)
instancia.set_property("nome", "João")
instancia.set_property("idade", 30)

# Chamar método
instancia.call_method("falar", [], context)
```

## 🚀 Performance

O executor é otimizado para:
- **Lookup de variável O(1)** via dicionário
- **Dispatch de nós O(1)** via registry
- **Call stack leve** apenas quando necessário

---

**Nota**: O executor é stateful. Para executar múltiplos programas isolados, crie novos interpreters ou limpe o contexto entre execuções.
