# relations.py — Sistema de Relações

Este módulo centraliza a lógica de relações entre objetos do interpretador (AST, ORM, dependências, etc).

## Funcionalidades
- Permite mapear relações simples (um-para-muitos) e complexas (grafos).
- Interface simples baseada em dicionários e listas.

## Exemplo de uso
```python
from src.corplang.core.relations import relations

relations.add("pai", "filho1")
relations.add("pai", "filho2")
print(relations.get("pai"))  # ['filho1', 'filho2']
relations.remove("pai", "filho1")
```

## Extensão
- Para relações mais complexas, adicione métodos ou use bibliotecas externas.
- Documente sempre o padrão de uso para facilitar manutenção.
