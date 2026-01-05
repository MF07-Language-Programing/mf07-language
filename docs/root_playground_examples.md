# MF Language Quick Playground

Bem-vindo: abaixo você encontra cenários curtos e prontos para rodar com o `mf` CLI. Cada bloco mostra um uso idiomático que antes vivia em arquivos soltos na raiz. Copie um trecho para um arquivo `.mp` e execute com `mf run <arquivo>.mp`.

## Coleções rápidas (List/Map/Set/Stack/Queue)
```mp
from core.collections.list import List
from core.collections.map import Map
from core.collections.set import Set
from core.collections.stack import Stack
from core.collections.queue import Queue

intent main() {
    var nums = new List(null)
    nums.append(10)
    nums.append(20)
    print("List size", nums.size())
    for (var n in nums) { print("n=", n) }

    var people = new Map(null)
    people.put("name", "Alice")
    people.put("age", 30)
    for (var entry in people) { print(entry[0], entry[1]) }

    var uniq = new Set(null)
    uniq.add(1); uniq.add(1); uniq.add(2)
    print("Set size", uniq.size())

    var stack = new Stack(null)
    stack.push("A"); stack.push("B")
    print("Stack pop", stack.pop())

    var queue = new Queue(null)
    queue.enqueue(100); queue.enqueue(200)
    print("Queue dequeue", queue.dequeue())
}

main()
```

## Generics básicos
```mp
from core.collections.list import List
from core.collections.map import Map

intent main() {
    var ints = new List<int>(null)
    ints.append(1)
    ints.append(2)
    print("ints size", ints.size())

    var scores = new Map<string, int>(null)
    scores.put("age", 30)
    scores.put("score", 99)
    for (var entry in scores) { print(entry[0], entry[1]) }
}

main()
```

## Contrato genérico em runtime
```mp
from core.collections.list import List
from core.lang.exceptions import GenericContractError

intent main() {
    var list = new List<int>(null)
    list.append(10)
    try {
        list.append("invalid")
    } catch (e: GenericContractError) {
        print("Erro esperado:", e.message)
    }
}

main()
```

## Inspeção de generics (genericOf)
```mp
from core.collections.map import Map

intent main() {
    var m = new Map<string, int>(null)
    var g = genericOf(m)
    print("Tem K?", "K" in g, "Tem V?", "V" in g)
    if ("K" in g) { print("K:", g["K"]) }
    if ("V" in g) { print("V:", g["V"]) }
}

main()
```

## Construtores e campos
```mp
class TestClass<K, V> {
    var field: string

    intent constructor() {
        sout("ctor: field before = " + this.field)
        this.field = "updated"
        sout("ctor: field after = " + this.field)
    }

    intent getField(): string {
        return this.field
    }
}

var inst = new TestClass()
sout("field via getter: " + inst.getField())
```

## Iteration protocol custom
```mp
from core.lang.Iterable import Iterable
from core.lang.Iterator import Iterator

class CounterIterator implements Iterator<int> {
    private var cur: int
    private var end: int
    intent constructor(start: int, end: int) { this.cur = start; this.end = end }
    intent hasNext() -> bool { return this.cur < this.end }
    intent next() -> int { if (not this.hasNext()) { return null } var v = this.cur; this.cur = this.cur + 1; return v }
}

class Range implements Iterable<int> {
    private var start: int; private var end: int
    intent constructor(start: int, end: int) { this.start = start; this.end = end }
    intent __iter__() -> Iterator<int> { return new CounterIterator(this.start, this.end) }
}

intent main() {
    var r = new Range(1, 4)
    for (var x in r) { print("x=", x) }
}

main()
```

## Null-friendly concat
```mp
var f = null
sout("Type: " + type(f))
var msg = "Test: " + f
sout("Msg: " + msg)
```

## Exceções idiomáticas
```mp
from core.lang.exceptions import GenericContractError

intent main() {
    try {
        throw new GenericContractError("boom")
    } catch (e: GenericContractError) {
        print("caught", e.message)
    }
}

main()
```

## Data/hora (mf.datetime)
```mp
sout("Testing mf.datetime access...")
var today = mf.datetime.today()
sout("today value: " + today)
```

## Demonstração completa de coleções
```mp
from core.collections import Map, List, Stack, Queue, Set

intent main() {
    var nums = new List()
    nums.append(10); nums.append(20); nums.append(30)
    print("List", nums, "size", nums.size())

    var myMap = new Map()
    myMap.put("name", "Alice"); myMap.put("age", 25)
    print("Map keys", myMap.keys())

    var stack = new Stack(); stack.push(100); stack.push(200)
    print("Stack pop", stack.pop())

    var queue = new Queue(); queue.enqueue("first"); queue.enqueue("second")
    print("Queue dequeue", queue.dequeue())

    var uniq = new Set(); uniq.add(1); uniq.add(1); uniq.add(2)
    print("Set size", uniq.size())
}

main()
```
