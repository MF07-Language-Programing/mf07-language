# memory.py — Gerenciamento de Memória

Este módulo provê utilitários para monitoramento de uso de memória e integração com garbage collection no interpretador Corplang/MF07.

## Funcionalidades
- Monitora uso de memória em tempo real (`tracemalloc`).
- Permite definir limites de uso (em MB).
- Loga criação/destruição de objetos relevantes.
- Suporte a weak references para evitar vazamentos.

## Exemplo de uso
```python
from src.corplang.core.memory import memory_manager, track_object

obj = ... # qualquer objeto
ref = track_object(obj, label="MeuObjeto")
current, peak = memory_manager.check_memory()
print(f"Memória atual: {current/1024/1024:.2f} MB")
```

## Extensão
- Para adicionar hooks de profiling, modifique `MemoryManager`.
- Para logs automáticos em AST, chame `track_object` ao criar nós.
