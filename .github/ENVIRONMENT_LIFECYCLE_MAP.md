# Mapa Completo de Ciclo de Vida de Environment

## Todos os pontos de criação de `Environment(...)`

### 1. **interpreter.py:271** | `_ensure_builtins()`
```python
self.global_env = Environment()
```
- **Responsabilidade:** Criar environment global vazio para builtins
- **Classificação:** ✅ **NECESSÁRIO**
- **Natureza:** Anchor semântico - representa escopo de builtins
- **Invariante:** Deve ser criado uma única vez, nunca recriado
- **Parent:** None (raiz)

---

### 2. **interpreter.py:328** | `_import_module()`
```python
env = Environment()
ctx = ExecutionContext(
    interpreter=self,
    environment=env,
    ...
)
self.execute(ast, ctx)
exports = dict(env.variables)
```
- **Responsabilidade:** Criar environment isolado para módulo
- **Classificação:** ⚠️ **PARCIALMENTE CORRETO**
- **Problema:** `env` não tem parent = None
  - Deveria ser `Environment(parent=self.global_env)` para ter builtins acessíveis
  - Atualmente builtins é fallback via `interpreter.global_env` mutation
- **Natureza:** Environment de escopo de módulo
- **Parent:** Deve ser `self.global_env` (builtins)
- **Consequência do Bug:** `class_ref._env` fica referenciando environment sem acesso a builtins

---

### 3. **context.py:78** | `ExecutionContext.child()`
```python
env = Environment(self.environment)
```
- **Responsabilidade:** Criar novo escopo local para bloco/função
- **Classificação:** ✅ **NECESSÁRIO**
- **Natureza:** Escopo lexical - parent é escopo anterior
- **Parent:** `self.environment` (correto - herda do contexto pai)
- **Uso:** Loops, if/else, funções, blocos

---

### 4. **executor/__init__.py:70** | `execute()` top-level
```python
env = getattr(current, "global_env", None) or Environment()
```
- **Responsabilidade:** Fallback se não houver global_env
- **Classificação:** ⚠️ **REDUNDANTE**
- **Problema:** Não deveria estar aqui - global_env sempre existe após `_ensure_builtins()`
- **Ação:** Remover, usar `current.global_env` direto

---

### 5. **core/utils.py:65** | `bind_and_exec()` - NOVO
```python
method_env = Environment(closure_env)
for k, v in bound.items():
    method_env.define(k, v)
child = ctx.spawn(method_env)
```
- **Responsabilidade:** Criar environment com parâmetros ligados
- **Classificação:** ✅ **NECESSÁRIO** (correctamente implementado)
- **Natureza:** Escopo de método - locals + closure
- **Parent:** `closure_env` (module environment onde método foi definido)
- **Fluxo:** method_env → closure_env (module) → global_env (builtins)

---

### 6. **objects.py:35** | `CorpLangFunction.__call__()` - async
```python
env = Environment(self._closure)
```
- **Responsabilidade:** Environment para execução de função async
- **Classificação:** ✅ **NECESSÁRIO**
- **Natureza:** Escopo de função - closure como parent
- **Parent:** `self._closure` (correto)

---

### 7. **objects.py:54** | `CorpLangFunction.__call__()` - sync fallback
```python
env = Environment(self.closure)
```
- **Responsabilidade:** Backup para função regular (não deveria estar aqui?)
- **Classificação:** ❓ **SUSPEITO**
- **Análise:** Parece duplicado com `bind_and_exec`
- **Ação:** Necessário verificar se `CorpLangFunction` ainda é usado

---

### 8. **objects.py:196** | `ClassObject.get_static()` - métodos estáticos
```python
env = Environment(closure_env)
return bind_and_exec(
    self.interpreter,
    declare,
    env,
    a,
    kw,
    self.interpreter.root_context,
    class_ref=self,
)
```
- **Responsabilidade:** Criar environment para método estático
- **Classificação:** ❌ **CONCEITUALMENTE ERRADO**
- **Problema:** 
  - Cria `Environment(closure_env)` vazio
  - Passa como primeiro arg de `bind_and_exec`
  - `bind_and_exec` cria **OUTRO** `Environment()` em cima dele
  - Resultado: `closure_env` é indireto, não direto
- **Ação:** Passar `closure_env` direto para `bind_and_exec`, não envolver em Environment

---

### 9. **objects.py:289** | `ClassObject.get_static()` - async await
```python
env = Environment(closure_env)
```
- **Classificação:** ❌ **CONCEITUALMENTE ERRADO**
- **Problema:** Mesmo que #8
- **Ação:** Remover, deixar `bind_and_exec` cuidar

---

### 10. **objects.py:398** | `ClassObject.get()` - static methods
```python
env = Environment(self.interpreter.global_env)
```
- **Responsabilidade:** Environment para método estático
- **Classificação:** ❌ **ERRADO**
- **Problema:** 
  - Usa `interpreter.global_env` diretamente
  - Deveria usar `self._env` (module environment onde classe foi definida)
- **Ação:** Substituir por `self._env`

---

### 11. **objects.py:423** | `ClassObject.get()` - static methods (fallback)
```python
env = Environment(self.interpreter.global_env)
```
- **Classificação:** ❌ **ERRADO**
- **Problema:** Mesmo que #10
- **Ação:** Substituir por `self._env`

---

### 12. **oop.py:329** | Super executor
```python
env = Environment(interpreter.global_env)
for pname, value in bound.items():
    env.define(pname, value)
env.define("this", this)

old_env = interpreter.global_env
interpreter.global_env = env
child_ctx = interpreter.root_context.spawn(env)
```
- **Responsabilidade:** Executar constructor do super
- **Classificação:** ❌ **DUPLO ERRO**
- **Problema 1:** Cria environment com `global_env` como parent
- **Problema 2:** Substitui `interpreter.global_env` (mutação global)
- **Ação:** Reescrever usando `bind_and_exec` diretamente

---

## Mapa Visual de Hierarquia Correta

```
INÍCIO
  ↓
global_env = Environment()  [BUILTINS - imutável]
  ↓
_import_module("map.mp"):
  ├─ module_env = Environment(parent=global_env)
  ├─ Executa imports → console definido em module_env.variables
  ├─ class Map criada:
  │  └─ Map._env = module_env [ANCHOR SEMÂNTICO]
  └─ Retorna exports

Depois:
  myMap = new Map()
  ├─ Constructor:
  │  └─ method_env = Environment(parent=Map._env)
  │     └─ Executa constructor body
  │
  myMap.put("key", "value"):
  ├─ put method:
  │  └─ method_env = Environment(parent=Map._env)
  │     └─ Acessa console via parent chain:
  │        method_env → Map._env (module) → global_env (builtins) ✅
```

---

## Padrão de Resolução Correto

### QUANDO criar novo Environment:

1. **Locals para método/função:**
   ```python
   method_env = Environment(closure_env)
   method_env.define("param1", arg1)
   method_env.define("param2", arg2)
   method_env.define("this", instance)
   ```
   ✅ Parent = closure (module environment)

2. **Bloco local (if/while/for):**
   ```python
   block_env = Environment(parent=current_env)
   ```
   ✅ Parent = ambiente anterior

### QUANDO NÃO criar:

1. ❌ Não envolver closure em `Environment()` vazio antes de passar
2. ❌ Não criar `Environment()` se não há locals para adicionar
3. ❌ Não usar `interpreter.global_env` como fallback em criação de Environment
4. ❌ Não substituir `interpreter.global_env` durante execução

---

## Estados de Bug Atuais

| Local | Tipo | Sintoma | Impacto |
|-------|------|---------|---------|
| interpreter.py:328 | Missing parent | `env = Environment()` sem parent | Métodos não veem builtins via closure |
| objects.py:196,289 | Wrapper redundante | `Environment(closure_env)` | Intermediário vazio degrada lookup |
| objects.py:398,423 | Wrong fallback | Usa `global_env` em vez de `_env` | Métodos estáticos perdem closure |
| oop.py:329-362 | Global mutation | `interpreter.global_env = env` | Race condition potencial |
| executor/__init__.py:70 | Redundante | Fallback desnecessário | Complexidade sem ganho |

---

## Redesenho Mínimo Necessário

### ✅ Mantém:
- `global_env = Environment()` como anchor
- `class_ref._env` imutável após criação
- `Environment.parent` chain para lookup lexical
- `bind_and_exec` como entry point para method execution

### ❌ Remove:
- Wrapping intermediário de `Environment()`
- Mutações de `interpreter.global_env`
- Fallbacks desnecessários
- Super executor com mutação global

### 🔧 Corrige:
- `_import_module()` → `Environment(parent=global_env)`
- `ClassObject.get_static()` → passa `self._env` direto
- Super executor → usa `bind_and_exec`

---

## Sequência de Implementação

1. **Fix #1:** `_import_module()` - add `parent=self.global_env`
2. **Fix #2:** `ClassObject.get_static()` - remove `Environment()` wrapper
3. **Fix #3:** `ClassObject.get()` - use `self._env` não `global_env`
4. **Fix #4:** Super executor - reescrever com `bind_and_exec`
5. **Fix #5:** Remover redundância em `executor/__init__.py`
6. **Validate:** Rodar full test suite
