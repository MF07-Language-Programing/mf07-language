# Module Registry - Sistema de Registro de Módulos

O **Module Registry** é um componente central que mantém o controle de todos os módulos carregados durante a execução de um programa Corplang. Ele funciona como um "banco de dados" em memória que mapeia nomes de módulos para seus caminhos, exports e metadados.

## 🎯 Para que serve?

Imagine que seu programa `.mp` importa vários módulos:

```corplang
import List from collections.list
import Map from collections.map
import Env from system.env
import minhaLib from lib.utils
```

O **Module Registry** garante que:
- ✅ Cada módulo seja carregado **apenas uma vez** (cache)
- ✅ Você possa **verificar** se um módulo já foi carregado
- ✅ Imports subsequentes **reutilizem** o módulo em cache
- ✅ Conflitos de nome sejam **detectados**

## 📖 Uso básico

### Criar um registry

```python
from src.corplang.core.module_registry import ModuleRegistry

registry = ModuleRegistry()
```

### Registrar um módulo

```python
registry.register(
    name="collections.list",
    path="/stdlib/core/collections/list.mp",
    exports={"List", "ImmutableList"}
)
```

### Verificar se módulo foi carregado

```python
if registry.is_loaded_by_name("collections.list"):
    print("Módulo collections.list já está carregado!")

if registry.is_loaded_by_path("/stdlib/core/collections/list.mp"):
    print("Arquivo já foi carregado!")
```

### Obter informações do módulo

```python
# Por nome
path = registry.get_path("collections.list")
print(f"Módulo carregado de: {path}")

exports = registry.get_exports("collections.list")
print(f"Exports: {exports}")

# Por caminho
nome = registry.get_name_by_path("/stdlib/core/collections/list.mp")
print(f"Nome do módulo: {nome}")
```

## 🔧 API completa

### `register(name, path, exports=None)`

Registra um novo módulo no registry.

```python
registry.register(
    name="meu.modulo",
    path="/projeto/lib/meu_modulo.mp",
    exports={"MinhaClasse", "minha_funcao"}
)
```

**Parâmetros:**
- `name` (str): Nome lógico do módulo (ex: `collections.list`)
- `path` (str): Caminho absoluto do arquivo `.mp`
- `exports` (set|list|None): Símbolos exportados pelo módulo

**Comportamento:**
- Se o módulo já existir, **atualiza** as informações
- Normaliza paths (resolve `..`, symlinks, etc.)
- Registra bidirecionalmente (nome→path e path→nome)

### `is_loaded_by_name(name) -> bool`

Verifica se módulo foi carregado pelo nome lógico.

```python
if not registry.is_loaded_by_name("collections.list"):
    # Carregar módulo
    load_module("collections.list")
```

### `is_loaded_by_path(path) -> bool`

Verifica se módulo foi carregado pelo caminho do arquivo.

```python
if not registry.is_loaded_by_path("/stdlib/core/collections/list.mp"):
    # Carregar arquivo
    load_file("/stdlib/core/collections/list.mp")
```

### `get_path(name) -> Optional[str]`

Retorna o caminho do arquivo para um módulo registrado.

```python
path = registry.get_path("collections.list")
# "/stdlib/core/collections/list.mp"
```

### `get_name_by_path(path) -> Optional[str]`

Retorna o nome lógico de um módulo dado seu caminho.

```python
nome = registry.get_name_by_path("/stdlib/core/collections/list.mp")
# "collections.list"
```

### `get_exports(name) -> Optional[set]`

Retorna os símbolos exportados por um módulo.

```python
exports = registry.get_exports("collections.list")
# {"List", "ImmutableList", "ListIterator"}
```

### `list_all_modules() -> List[str]`

Lista todos os módulos registrados.

```python
modulos = registry.list_all_modules()
# ["collections.list", "collections.map", "system.env", ...]
```

### `clear()`

Limpa todos os módulos registrados.

```python
registry.clear()
# Útil para testes ou reinicialização
```

## 💡 Padrões de uso

### Evitar duplicação de carga

```python
def carregar_modulo(nome: str, registry: ModuleRegistry):
    if registry.is_loaded_by_name(nome):
        print(f"Módulo {nome} já carregado, usando cache")
        return registry.get_path(nome)
    
    # Resolver caminho do módulo
    caminho = resolver_import(nome)
    
    # Carregar e parsear
    ast = parse_file(caminho)
    exports = extract_exports(ast)
    
    # Registrar no registry
    registry.register(nome, caminho, exports)
    
    # Executar
    execute(ast)
    
    return caminho
```

### Integração com loader

```python
from src.corplang.core.loader import load_core_modules_from_manifest
from src.corplang.core.module_registry import ModuleRegistry

registry = ModuleRegistry()

summary = load_core_modules_from_manifest(
    core_dir="stdlib/core",
    import_resolver=my_resolver,
    module_loader=my_loader,
    module_registry=registry  # Passa o registry
)

# Agora o registry contém todos os módulos carregados
print(f"Módulos no registry: {registry.list_all_modules()}")
```

### Diagnóstico de imports

```python
def diagnosticar_imports(programa_path: str, registry: ModuleRegistry):
    """Analisa quais imports de um programa já estão carregados."""
    imports = extract_imports_from_file(programa_path)
    
    print(f"Imports encontrados: {len(imports)}")
    for imp in imports:
        if registry.is_loaded_by_name(imp):
            print(f"  ✓ {imp} - já carregado")
        else:
            print(f"  ✗ {imp} - precisa carregar")
```

## 🏗️ Estrutura interna

O registry mantém três dicionários internos:

```python
class ModuleRegistry:
    def __init__(self):
        self._modules = {}           # nome -> {path, exports, metadata}
        self._path_to_name = {}      # path -> nome
        self._name_to_exports = {}   # nome -> set(exports)
```

Isso permite lookups O(1) em todas as direções:
- Nome → Path: `_modules[nome]["path"]`
- Path → Nome: `_path_to_name[path]`
- Nome → Exports: `_name_to_exports[nome]`

## 🔍 Exemplo completo

```python
from src.corplang.core.module_registry import ModuleRegistry

# Criar registry
registry = ModuleRegistry()

# Simular carregamento de módulos
modulos = [
    ("collections.list", "/stdlib/core/collections/list.mp", {"List"}),
    ("collections.map", "/stdlib/core/collections/map.mp", {"Map"}),
    ("system.env", "/stdlib/core/system/env.mp", {"Env"}),
]

for nome, path, exports in modulos:
    registry.register(nome, path, exports)
    print(f"Registrado: {nome}")

# Verificar status
print(f"\nMódulos carregados: {len(registry.list_all_modules())}")

# Buscar informações
nome_procurado = "collections.list"
if registry.is_loaded_by_name(nome_procurado):
    path = registry.get_path(nome_procurado)
    exports = registry.get_exports(nome_procurado)
    print(f"\n{nome_procurado}:")
    print(f"  Path: {path}")
    print(f"  Exports: {exports}")

# Reverse lookup
path_procurado = "/stdlib/core/system/env.mp"
nome = registry.get_name_by_path(path_procurado)
print(f"\nArquivo {path_procurado} é o módulo: {nome}")
```

**Saída:**
```
Registrado: collections.list
Registrado: collections.map
Registrado: system.env

Módulos carregados: 3

collections.list:
  Path: /stdlib/core/collections/list.mp
  Exports: {'List'}

Arquivo /stdlib/core/system/env.mp é o módulo: system.env
```

## 🚀 Performance

- **Registro**: O(1) — dicionários Python
- **Lookup por nome**: O(1)
- **Lookup por path**: O(1)
- **Listar todos**: O(n)

## 🛡️ Thread-safety

⚠️ **Nota**: O registry atual **não é thread-safe**. Se precisar usar em contexto multi-thread:

```python
import threading

class ThreadSafeModuleRegistry(ModuleRegistry):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
    
    def register(self, name, path, exports=None):
        with self._lock:
            super().register(name, path, exports)
    
    def is_loaded_by_name(self, name):
        with self._lock:
            return super().is_loaded_by_name(name)
    
    # ... outros métodos com lock
```

## 📦 Integração com o sistema de imports

O registry trabalha em conjunto com o **ImportManager**:

1. ImportManager resolve o caminho de um import
2. Verifica no registry se já foi carregado
3. Se não, carrega o arquivo e extrai exports
4. Registra no registry
5. Próximos imports do mesmo módulo usam o registry

---

**Dica profissional**: Sempre use um único registry global compartilhado por todo o runtime. Múltiplos registries podem causar duplicação de carga de módulos.
