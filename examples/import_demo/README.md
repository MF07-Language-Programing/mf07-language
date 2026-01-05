# Import Demo

Três exemplos para testar imports: módulo local, stdlib com prefixo `core.*` e stdlib com prefixo `mf.*`.

## Arquivos
- [with_import.mp](with_import.mp): usa `from core.collections.list import List` da stdlib.
- [with_mf_prefix.mp](with_mf_prefix.mp): usa `from mf.core.collection.list import List` (prefixo `mf.` + singular `collection`).
- [no_import.mp](no_import.mp): cálculo simples sem imports.

## Como rodar
```bash
# Stdlib (sem prefixo)
./mf run examples/import_demo/with_import.mp

# Stdlib (com prefixo mf.)
./mf run examples/import_demo/with_mf_prefix.mp

# Sem import
./mf run examples/import_demo/no_import.mp
```

## Notas técnicas
- O normalizador aceita `mf.core.collection.*` e converte para `core.collections.*` automaticamente.
- A stdlib é descoberta pela versão ativa (`CORPLANG_ACTIVE_VERSION`) ou fallback para dev.
- Módulos restritos (ex: `core.system.os`) são bloqueados via manifest `security: restricted`.

