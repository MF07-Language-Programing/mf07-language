# MF07-LANGUAGE: DESIGN DE COLLECTIONS E ITERAÇÃO
## Documento Arquitetural — Language Designer Perspective

---

## PARTE 1: ANÁLISE DA LINGUAGEM ATUAL

### 1.1 SINTAXE E ESTRUTURAS FUNDAMENTAIS

**Classes e Generics**
```mp
class Map<K, V> {
    private var data
    intent constructor(keyType: Optional<K> = null) { }
    intent put(key: K, value: V): boolean { }
}
```

**Observações:**
- Generics `<T>` suportados na declaração
- Sem validação de tipo em tempo de compilação (tipagem gradual/dinâmica)
- `intent` = métodos
- Modificadores: `private`, `protected`, `static`
- Suporta herança (`extends`) e interfaces (`implements`)

**Loops Suportados**
1. `for (init; condition; update)` — estilo C
2. `for (var x in iterable)` — itera sobre **keys** (dict) ou **valores** (list)
3. `for (var x of iterable)` — itera sobre **values** (dict) ou **elementos** (list)
4. `while (condition)`

### 1.2 RUNTIME: COMO ITERAÇÃO FUNCIONA ATUALMENTE

**ForInExecutor** (control_flow.py:90-136)
```python
def execute(self, node, context):
    iterable_value = resolve_node_value(node.iterable, context)
    
    if isinstance(iterable_value, dict):
        iterable = list(iterable_value.keys())  # ← keys para dict
    elif isinstance(iterable_value, InstanceObject):
        raw_getter = iterable_value.get("__raw__")
        if callable(raw_getter):
            raw_data = raw_getter()  # ← extrai dados internos
            iterable = list(raw_data.keys() if isinstance(raw_data, dict) else raw_data)
    else:
        iterable = list(iterable_value)
    
    for item in iterable:
        child = context.child({var_name: item})
        context.interpreter.execute(node.body, child)
```

**ForOfExecutor** (control_flow.py:137-178)
- Similar, mas extrai `values()` de dict em vez de keys
- Para InstanceObject, tenta `__raw__()` primeiro

**PROBLEMA IDENTIFICADO:**
- Não existe protocolo de iteração explícito (`__iter__`, `__next__`)
- Runtime depende de hack `__raw__()` para extrair dados internos
- Não há suporte a iteradores preguiçosos ou customizados
- Mistura responsabilidades: ForInExecutor não deveria saber sobre InstanceObject

---

## PARTE 2: CONTRATOS E PROTOCOLOS NECESSÁRIOS

### 2.1 MODELO CONCEITUAL: PROTOCOLO DE ITERAÇÃO

#### **Contrato 1: Iterable<T>**
Objeto que pode ser iterado.

```mp
interface Iterable<T> {
    """
    Protocolo de iteração. Qualquer objeto que implemente este contrato
    pode ser usado em loops `for..in` e `for..of`.
    """
    intent iterator() -> Iterator<T>
}
```

**Semântica:**
- `iterator()` deve retornar um novo Iterator a cada chamada
- Permite múltiplas iterações simultâneas
- Estado de iteração pertence ao Iterator, não ao Iterable

#### **Contrato 2: Iterator<T>**
Objeto que controla o estado da iteração.

```mp
interface Iterator<T> {
    """
    Cursor de iteração. Mantém posição atual e fornece acesso sequencial.
    """
    intent hasNext() -> bool
    intent next() -> T
}
```

**Semântica:**
- `hasNext()`: verifica se há mais elementos (O(1))
- `next()`: retorna próximo elemento e avança cursor
- `next()` em iterador exausto deve lançar exceção ou retornar null (decisão de design)
- Iterator é stateful, não deve ser reutilizado após exaustão

#### **Contrato 3: Collection<T>**
Base para todas as collections concretas.

```mp
interface Collection<T> extends Iterable<T> {
    """
    Contrato universal para coleções mutáveis.
    """
    intent size() -> int
    intent isEmpty() -> bool
    intent clear()
    intent contains(value: T) -> bool
    intent toArray() -> Array<T>
}
```

**Decisões:**
- `Collection` estende `Iterable` — toda collection é iterável
- Não assume ordem (diferente de List)
- Mutável por padrão (Immutable* para versões imutáveis)

---

### 2.2 INTEGRAÇÃO COM RUNTIME

**HOOKS QUE DEVEM EXISTIR:**

1. **ForInExecutor deve buscar `__iter__`**
   ```python
   # Pseudocódigo Python no runtime
   def execute_for_in(node, context):
       iterable_value = resolve(node.iterable)
       
       # Tentar protocolo de iteração
       if hasattr(iterable_value, 'get'):  # InstanceObject
           iter_method = iterable_value.get('__iter__')
           if callable(iter_method):
               iterator = iter_method()  # chama iterator()
               while True:
                   has_next = iterator.get('hasNext')()
                   if not has_next:
                       break
                   item = iterator.get('next')()
                   execute_body(item)
       # Fallback para tipos nativos (list, dict)
       else:
           for item in iterable_value:
               execute_body(item)
   ```

2. **Fallback para tipos nativos (list, dict, str)**
   - dict → itera keys (for..in) ou values (for..of)
   - list → itera elementos
   - str → itera caracteres

3. **Erro explícito se não iterável**
   ```mp
   TypeError: Object <MyClass> is not iterable (missing __iter__ method)
   ```

---

## PARTE 3: MODELAGEM DAS COLLECTIONS

### 3.1 List<T>: LISTA DINÂMICA

**Responsabilidades:**
- Armazenamento ordenado de elementos
- Acesso por índice (O(1))
- Inserção/remoção ao final (O(1) amortizado)
- Inserção/remoção no meio (O(n))

**Contrato:**
```mp
class List<T> implements Collection<T> {
    private var data: Array<T>  # array nativo Python
    private var elementType: string
    
    intent constructor(elementType: Optional<string> = null)
    intent append(item: T) -> bool
    intent get(index: int) -> T
    intent set(index: int, value: T)
    intent remove(index: int) -> T
    intent indexOf(item: T) -> int
    intent size() -> int
    intent iterator() -> Iterator<T>  # ← obrigatório
}
```

**Decisões de Implementação:**
- `data` é Python list (`[]`) direto — zero overhead
- Validação de tipo opcional (se `elementType` fornecido)
- `iterator()` retorna `ListIterator` encapsulando índice interno

**Iteração:**
```mp
intent iterator() -> Iterator<T> {
    return new ListIterator<T>(this.data)
}

class ListIterator<T> implements Iterator<T> {
    private var data: Array<T>
    private var index: int = 0
    
    intent hasNext() -> bool {
        return this.index < len(this.data)
    }
    
    intent next() -> T {
        if (not this.hasNext()) {
            throw new Error("Iterator exausto")
        }
        var value = this.data[this.index]
        this.index = this.index + 1
        return value
    }
}
```

---

### 3.2 Map<K, V>: DICIONÁRIO CHAVE-VALOR

**Responsabilidades:**
- Mapeamento key → value
- Acesso por chave (O(1) esperado)
- Iteração sobre keys, values ou entries

**Contrato:**
```mp
class Map<K, V> implements Iterable<K> {  # itera keys por padrão
    private var data: dict
    
    intent constructor(keyType: Optional<string> = null, 
                      valueType: Optional<string> = null)
    intent put(key: K, value: V) -> bool
    intent get(key: K) -> V | null
    intent has(key: K) -> bool
    intent remove(key: K) -> bool
    intent size() -> int
    intent clear()
    
    # Iteração
    intent iterator() -> Iterator<K>     # itera keys
    intent keys() -> Iterator<K>
    intent values() -> Iterator<V>
    intent entries() -> Iterator<Entry<K,V>>
}
```

**Decisão:** Map **não** implementa `Collection<T>` porque não tem tipo de elemento único (tem K e V).

**Iteração de Map:**
```mp
# for..in deve iterar keys (como Python dict)
for (var key in myMap) {
    print(key)  # "name", "age"
}

# for..of deve iterar entries
for (var entry of myMap.entries()) {
    print(entry.key, entry.value)
}
```

---

### 3.3 Set<T>: CONJUNTO SEM DUPLICATAS

**Responsabilidades:**
- Armazenamento único (sem duplicatas)
- Verificação de pertinência (O(1) se usar hash)
- Operações de conjunto (union, intersect, diff)

**Contrato:**
```mp
class Set<T> implements Collection<T> {
    private var data: Array<T>  # ou dict se quiser O(1)
    
    intent add(element: T) -> bool
    intent has(element: T) -> bool
    intent remove(element: T) -> bool
    intent size() -> int
    intent iterator() -> Iterator<T>
    
    # Operações de conjunto
    intent union(other: Set<T>) -> Set<T>
    intent intersect(other: Set<T>) -> Set<T>
    intent difference(other: Set<T>) -> Set<T>
}
```

**Implementação:**
- Usar array simples + busca linear (O(n)) — simples, funciona
- **OU** usar dict com keys = elementos, values = true (O(1)) — performance

---

### 3.4 Stack<T>: PILHA LIFO

**Responsabilidades:**
- Push/pop em uma extremidade
- LIFO (last in, first out)

**Contrato:**
```mp
class Stack<T> implements Iterable<T> {
    private var data: Array<T>
    
    intent push(item: T)
    intent pop() -> T
    intent peek() -> T
    intent size() -> int
    intent isEmpty() -> bool
    intent iterator() -> Iterator<T>  # topo → base
}
```

---

### 3.5 Queue<T>: FILA FIFO

**Responsabilidades:**
- Enqueue no fim, dequeue no início
- FIFO (first in, first out)

**Contrato:**
```mp
class Queue<T> implements Iterable<T> {
    private var data: Array<T>
    
    intent enqueue(item: T)
    intent dequeue() -> T
    intent peek() -> T
    intent size() -> int
    intent iterator() -> Iterator<T>  # início → fim
}
```

---

## PARTE 4: ARQUITETURA DE IMPLEMENTAÇÃO

### 4.1 DIVISÃO RUNTIME vs LINGUAGEM

| Componente | Implementação | Justificativa |
|------------|---------------|---------------|
| **Protocolo de iteração** | 100% Runtime | ForInExecutor/ForOfExecutor devem reconhecer `__iter__` |
| **Iterator interface** | 100% Linguagem | Contrato puro, sem lógica especial |
| **Iterable interface** | 100% Linguagem | Contrato puro |
| **Collection interface** | 100% Linguagem | Base para todas as collections |
| **List<T>** | 90% Linguagem<br>10% Runtime (se precisar .append otimizado) | Wrapper fino sobre list Python |
| **Map<K,V>** | 90% Linguagem<br>10% Runtime (se precisar dict otimizado) | Wrapper fino sobre dict Python |
| **Set<T>** | 100% Linguagem | Implementação pura, sem otimização crítica |
| **Stack/Queue** | 100% Linguagem | Abstrações sobre List |

**Decisão crítica:** Manter collections o mais puras possível na linguagem, evitando dependências do runtime.

---

### 4.2 ESTRUTURA DE MÓDULOS

```
src/corplang/stdlib/core/
├── lang/
│   ├── Iterable.mp          # interface Iterable<T>
│   ├── Iterator.mp          # interface Iterator<T>
│   └── Collection.mp        # interface Collection<T>
│
├── collections/
│   ├── List.mp              # class List<T>
│   ├── ListIterator.mp      # class ListIterator<T>
│   ├── Map.mp               # class Map<K,V>
│   ├── MapIterator.mp       # class MapIterator<K> (keys)
│   ├── Set.mp               # class Set<T>
│   ├── SetIterator.mp       # class SetIterator<T>
│   ├── Stack.mp             # class Stack<T>
│   ├── Queue.mp             # class Queue<T>
│   └── Entry.mp             # class Entry<K,V> (para Map.entries())
│
└── collections/immutable/
    ├── ImmutableList.mp
    ├── ImmutableMap.mp
    └── ImmutableSet.mp
```

**Princípios:**
1. `lang/` contém contratos fundamentais (interfaces)
2. `collections/` contém implementações concretas
3. Cada collection tem seu Iterator dedicado
4. Imports: `from core.lang import Iterable, Iterator, Collection`

---

### 4.3 IMPLEMENTAÇÃO DO PROTOCOLO DE ITERAÇÃO NO RUNTIME

**Modificação necessária em `ForInExecutor`:**

```python
class ForInExecutor(NodeExecutor):
    def execute(self, node, context):
        iterable_value = resolve_node_value(node.iterable, context)
        
        # 1. Tentar protocolo de iteração (__iter__)
        if isinstance(iterable_value, InstanceObject):
            try:
                iter_method = iterable_value.get('__iter__')
                if callable(iter_method):
                    iterator = iter_method()
                    return self._iterate_protocol(iterator, node, context)
            except:
                pass  # fallback
        
        # 2. Fallback para tipos nativos
        if isinstance(iterable_value, dict):
            iterable = list(iterable_value.keys())
        elif isinstance(iterable_value, (list, tuple)):
            iterable = list(iterable_value)
        else:
            raise TypeError(f"Object is not iterable: {type(iterable_value)}")
        
        # 3. Executar corpo do loop
        for item in iterable:
            child = context.child({node.variable: item})
            context.interpreter.execute(node.body, child)
    
    def _iterate_protocol(self, iterator, node, context):
        """Executa iteração usando protocolo hasNext/next"""
        while True:
            has_next = iterator.get('hasNext')()
            if not has_next:
                break
            item = iterator.get('next')()
            child = context.child({node.variable: item})
            context.interpreter.execute(node.body, child)
```

---

## PARTE 5: REGRAS SEMÂNTICAS E CASOS DE USO

### 5.1 ITERAÇÃO EM COLLECTIONS

**List:**
```mp
var nums = new List<int>()
nums.append(1)
nums.append(2)
nums.append(3)

for (var x in nums) {  # itera elementos
    print(x)  # 1, 2, 3
}
```

**Map:**
```mp
var map = new Map<string, int>()
map.put("a", 1)
map.put("b", 2)

# for..in itera keys
for (var k in map) {
    print(k)  # "a", "b"
}

# for..of itera entries
for (var entry of map.entries()) {
    print(entry.key, entry.value)
}
```

**Set:**
```mp
var set = new Set<string>()
set.add("x")
set.add("y")

for (var item in set) {
    print(item)  # ordem indefinida
}
```

---

### 5.2 ITERADORES CUSTOMIZADOS

**Caso de uso: Range**
```mp
class Range implements Iterable<int> {
    private var start: int
    private var end: int
    private var step: int
    
    intent constructor(start: int, end: int, step: int = 1) {
        this.start = start
        this.end = end
        this.step = step
    }
    
    intent iterator() -> Iterator<int> {
        return new RangeIterator(this.start, this.end, this.step)
    }
}

class RangeIterator implements Iterator<int> {
    private var current: int
    private var end: int
    private var step: int
    
    intent constructor(start: int, end: int, step: int) {
        this.current = start
        this.end = end
        this.step = step
    }
    
    intent hasNext() -> bool {
        return this.current < this.end
    }
    
    intent next() -> int {
        var value = this.current
        this.current = this.current + this.step
        return value
    }
}

# Uso:
for (var i in new Range(0, 10, 2)) {
    print(i)  # 0, 2, 4, 6, 8
}
```

---

## PARTE 6: DECISÕES FINAIS E ROADMAP

### 6.1 DECISÕES CRÍTICAS

1. **Iteração é baseada em protocolo explícito**: `__iter__()` → Iterator
2. **Iterator é stateful**: hasNext/next (não exceptions como Python)
3. **Collections são wrappers finos**: Python list/dict embaixo, API rica em cima
4. **Generics são documentação**: Sem enforcement em runtime (por enquanto)
5. **Mutabilidade por padrão**: Immutable* para versões imutáveis
6. **for..in itera keys (Map) ou elementos (List)**
7. **for..of itera values (Map) ou elementos (List) — mesmo comportamento**

---

### 6.2 SEQUÊNCIA DE IMPLEMENTAÇÃO (SAFE ORDER)

**Fase 1: Contratos (100% seguros de implementar)**
1. `Iterable.mp` — interface pura
2. `Iterator.mp` — interface pura
3. `Collection.mp` — interface estendendo Iterable

**Fase 2: Runtime Hooks (modificações no Python)**
4. Atualizar `ForInExecutor` para reconhecer `__iter__`
5. Atualizar `ForOfExecutor` para reconhecer `__iter__`
6. Adicionar testes de integração

**Fase 3: Collections Básicas**
7. `ListIterator.mp` — implementação concreta de Iterator
8. `List.mp` — reescrever usando novo protocolo
9. `MapIterator.mp` — iterator para keys
10. `Map.mp` — reescrever usando novo protocolo

**Fase 4: Collections Complementares**
11. `Set.mp` e `SetIterator.mp`
12. `Stack.mp` (wrapper sobre List)
13. `Queue.mp` (wrapper sobre List)

**Fase 5: Estruturas Auxiliares**
14. `Entry.mp` — para Map.entries()
15. `Range.mp` — exemplo de Iterable customizado

**Fase 6: Validação**
16. Suite de testes abrangente
17. Benchmarks de performance
18. Documentação de uso

---

## PARTE 7: PONTOS DE ATENÇÃO (NÃO FAZER)

1. **NÃO copiar Python literalmente**: hasNext/next é melhor que StopIteration para esta linguagem
2. **NÃO usar herança excessiva**: interfaces são suficientes
3. **NÃO otimizar prematuramente**: simplicidade > micro-performance
4. **NÃO expor `_fields` ou `__raw__` diretamente**: encapsular sempre
5. **NÃO misturar responsabilidades**: Iterator ≠ Iterable ≠ Collection
6. **NÃO assumir tipagem estática**: generics são hints, não garantias
7. **NÃO quebrar compatibilidade**: manter fallback para código existente

---

## CONCLUSÃO

Este design estabelece uma **fundação sólida e extensível** para collections na MF07-Language:

✅ **Protocolo de iteração claro** (Iterable/Iterator)  
✅ **Collections com responsabilidades bem definidas**  
✅ **Separação limpa entre runtime e linguagem**  
✅ **Extensível para casos customizados** (Range, Lazy, etc)  
✅ **Performance previsível** (wrappers finos sobre Python)  
✅ **Semântica estável** (contratos explícitos)

**Próximo passo:** Implementar Fase 1 (interfaces) e validar design antes de prosseguir.
