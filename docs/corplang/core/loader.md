# Core Module Loader

O **Core Module Loader** é o sistema responsável por carregar automaticamente os módulos da biblioteca padrão (stdlib) quando um programa Corplang é executado. Ele funciona de forma semelhante ao sistema de módulos do Node.js, com cache inteligente e resolução de dependências.

## 📦 O que ele faz?

Quando você executa um arquivo `.mp`, o loader:

1. **Lê o manifest** (`stdlib/core/manifest.json`)
2. **Resolve cada módulo** usando o sistema de imports
3. **Verifica o cache** (`.corplang-cache/`) para ASTs pré-compiladas
4. **Carrega ou compila** cada módulo conforme necessário
5. **Registra** todos os módulos no registry global

## 🚀 Exemplo de uso no código Corplang

```corplang
# Você não precisa fazer nada especial!
# Os módulos core são carregados automaticamente:

import List from collections.list
import Env from system.env

var lista = new List<int>()
lista.add(10)
lista.add(20)

print("Módulos carregados: {lista.size()}")
```

## ⚙️ Cache de Módulos

O loader implementa um sistema de cache inspirado no Node.js:

```
.corplang-cache/
  ├── a4f92c1e.ast.pkl  # AST compilada de collections/list.mp
  ├── b8e3d9f2.ast.pkl  # AST compilada de system/env.mp
  └── ...
```

### Benefícios do cache:
- ✅ **Compilação ~10x mais rápida** em execuções subsequentes
- ✅ **Invalidação automática** quando o código-fonte muda
- ✅ **Zero configuração** necessária

## 🧹 Limpando o cache

Se precisar forçar recompilação completa:

```python
from src.corplang.core.loader import clear_module_cache

# Limpa todos os arquivos .ast.pkl
deleted_files = clear_module_cache("stdlib/core")
print(f"Cache limpo: {deleted_files} arquivos removidos")
```

## 📋 Estrutura do Manifest

O arquivo `manifest.json` define quais módulos carregar:

```json
{
  "modules": [
    "collections.list",
    "collections.map",
    "system.env",
    {
      "name": "internal.debug",
      "security": "restricted"
    }
  ]
}
```

**Campos suportados:**
- `name`: Nome do módulo (obrigatório)
- `path`: Caminho customizado (opcional)
- `security`: Marca módulos restritos que não devem ser carregados

## 🔧 API Python para integração

### Carregar módulos manualmente

```python
from src.corplang.core.loader import load_core_modules_from_manifest

summary = load_core_modules_from_manifest(
    core_dir="stdlib/core",
    import_resolver=my_import_resolver,
    module_loader=my_loader,
    fail_fast=False  # Continua mesmo se algum módulo falhar
)

print(f"✅ Carregados: {summary.loaded}")
print(f"❌ Falhas: {summary.failed}")
print(f"⛔ Restritos: {summary.restricted}")
```

### Verificar módulos carregados

```python
from src.corplang.core.loader import get_loaded_modules

modules = get_loaded_modules()
print(modules)
# {'core': ['collections.list', 'system.env', ...]}
```

### Acessar o registry

```python
from src.corplang.core.loader import get_default_module_registry

registry = get_default_module_registry()

if registry.is_loaded_by_name("collections.list"):
    path = registry.get_path("collections.list")
    print(f"Módulo carregado de: {path}")
```

## 🎯 Resolução de dependências

O loader extrai automaticamente exports e requires de cada módulo:

```corplang
# Em collections/list.mp
class List<T> {
    # ...
}

export List
```

O loader detecta:
- **Exports**: `List`
- **Requires**: nenhum (módulo raiz)

```corplang
# Em collections/sorted_list.mp
import List from collections.list

class SortedList<T> extends List<T> {
    # ...
}

export SortedList
```

O loader detecta:
- **Exports**: `SortedList`  
- **Requires**: `collections.list`

## 📊 Diagnóstico e debug

O loader gera logs estruturados úteis para debug:

```
INFO  | Core cache stats: 12 hits, 3 misses, 3 saved
WARN  | USING COMPILED MODULE CACHE: 12 modules from .corplang-cache
ERROR | Core module missing: collections.unknown path=<unresolved>
```

## 💡 Boas práticas

1. **Deixe o cache ativo** em produção (carregamento muito mais rápido)
2. **Limpe o cache** apenas quando:
   - Trocar de versão da linguagem
   - Problemas estranhos de compilação
   - Antes de fazer deploy de nova versão
3. **Use `fail_fast=False`** durante desenvolvimento para ver todos os erros de uma vez
4. **Use `fail_fast=True`** em produção para interromper na primeira falha

## 🔒 Segurança

Módulos marcados como `"security": "restricted"` são **automaticamente ignorados** pelo loader. Isso é útil para:

- Módulos internos de debug
- APIs experimentais instáveis
- Funcionalidades que requerem permissões especiais

---

**Nota**: O Core Module Loader está pronto para uso, mas não é ativado por padrão. Para ativá-lo, configure o runtime para chamar `load_core_modules_from_manifest` durante a inicialização.
