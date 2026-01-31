# Standard Library Examples — Complete Reference

Este documento consolida todos os exemplos do playground Corplang, organizados por módulo e use case. **Copy-paste pronto para rodar**.

---

## Collections (Core)

### List — Operações Básicas

```mp
from core.collections.list import List

intent main() {
    var nums = new List(null)
    nums.append(10)
    nums.append(20)
    nums.append(30)
    
    print("Size:", nums.size())        // Size: 3
    print("Contains 20?", nums.contains(20))  // true
    
    for (var n in nums) {
        print("→", n)
    }
}

main()
```

**Use case:** Armazenar coleção dinâmica sem tamanho fixo.

---

### Map — Key-Value Storage

```mp
from core.collections.map import Map

intent main() {
    var pessoa = new Map(null)
    pessoa.put("nome", "Alice")
    pessoa.put("idade", 30)
    pessoa.put("cargo", "Engenheira")
    
    print("Nome:", pessoa.get("nome"))       // Alice
    print("Idade:", pessoa.get("idade"))     // 30
    
    // Iterar pares
    for (var entrada in pessoa) {
        var chave = entrada[0]
        var valor = entrada[1]
        print(chave + "=" + valor)
    }
}

main()
```

**Use case:** Construir dicionários dinâmicos, armazenar configurações.

---

### Set — Unicidade Garantida

```mp
from core.collections.set import Set

intent main() {
    var uniq = new Set(null)
    uniq.add(1)
    uniq.add(1)  // Duplicado, será ignorado
    uniq.add(2)
    uniq.add(3)
    
    print("Size:", uniq.size())      // 3 (não 4)
    
    for (var n in uniq) {
        print("Único:", n)
    }
}

main()
```

**Use case:** Remover duplicatas, verificar existência O(1).

---

### Stack — LIFO (Last In, First Out)

```mp
from core.collections.stack import Stack

intent main() {
    var pilha = new Stack(null)
    pilha.push("A")
    pilha.push("B")
    pilha.push("C")
    
    print("Top:", pilha.peek())      // C (não remove)
    print("Pop:", pilha.pop())       // C (remove)
    print("Pop:", pilha.pop())       // B
    print("Size:", pilha.size())     // 1
}

main()
```

**Use case:** Desfazer/refazer, parsing de expressões.

---

### Queue — FIFO (First In, First Out)

```mp
from core.collections.queue import Queue

intent main() {
    var fila = new Queue(null)
    fila.enqueue("primeiro")
    fila.enqueue("segundo")
    fila.enqueue("terceiro")
    
    print("Dequeue:", fila.dequeue())     // primeiro
    print("Dequeue:", fila.dequeue())     // segundo
    print("Size:", fila.size())            // 1
}

main()
```

**Use case:** Processamento em ordem, simulação de fila.

---

## Generics — Type Safety

### Type Parameters Básicos

```mp
from core.collections.list import List

intent main() {
    // List de inteiros
    var ints = new List<int>(null)
    ints.append(1)
    ints.append(2)
    ints.append(3)
    print("Ints:", ints)
    
    // List de strings
    var nomes = new List<string>(null)
    nomes.append("Alice")
    nomes.append("Bob")
    nomes.append("Charlie")
    print("Nomes:", nomes)
}

main()
```

**Benefício:** Compile-time safety, sem runtime overhead.

---

### Map com Type Parameters

```mp
from core.collections.map import Map

intent main() {
    // Map<string, int> — Scores
    var scores = new Map<string, int>(null)
    scores.put("Alice", 95)
    scores.put("Bob", 87)
    scores.put("Charlie", 92)
    
    for (var entrada in scores) {
        var nome = entrada[0]
        var score = entrada[1]
        print(nome + " scored " + score)
    }
}

main()
```

---

### Generic Contract Enforcement

```mp
from core.collections.list import List
from core.lang.exceptions import GenericContractError

intent main() {
    var list = new List<int>(null)
    list.append(10)
    list.append(20)
    
    try {
        list.append("invalid")  // String, mas esperamos int
    } catch (e: GenericContractError) {
        print("Erro capturado:", e.message)
        print("Type checking funciona em runtime!")
    }
}

main()
```

**Benefício:** Validação de tipo mesmo em coleções dinâmicas.

---

### Inspecionar Tipos Genéricos (genericOf)

```mp
from core.collections.map import Map

intent main() {
    var map = new Map<string, int>(null)
    var tipos = genericOf(map)
    
    // Inspecionar parâmetros
    if ("K" in tipos) {
        print("Tipo de chave (K):", tipos["K"])  // string
    }
    
    if ("V" in tipos) {
        print("Tipo de valor (V):", tipos["V"])  // int
    }
}

main()
```

**Use case:** Metaprogramming, validação em runtime.

---

## Orientação a Objetos

### Classe com Constructor

```mp
class Pessoa {
    var nome: string
    var idade: int
    
    intent constructor(nome: string, idade: int) {
        this.nome = nome
        this.idade = idade
        print("Pessoa criada:", nome)
    }
    
    intent apresentar() -> string {
        return this.nome + " tem " + this.idade + " anos"
    }
}

intent main() {
    var p = new Pessoa("Alice", 30)
    print(p.apresentar())
}

main()
```

---

### Classe Genérica

```mp
class Caixa<T> {
    var conteudo: T
    
    intent constructor(item: T) {
        this.conteudo = item
    }
    
    intent abrir() -> T {
        return this.conteudo
    }
}

intent main() {
    var caixa_int = new Caixa<int>(42)
    var caixa_str = new Caixa<string>("Olá")
    
    print("Caixa int:", caixa_int.abrir())     // 42
    print("Caixa string:", caixa_str.abrir())  // Olá
}

main()
```

---

## Iteração Customizada

### Implementar Iterator Protocol

```mp
from core.lang.Iterator import Iterator
from core.lang.Iterable import Iterable

class ContadorIterador implements Iterator<int> {
    var inicio: int
    var fim: int
    var atual: int
    
    intent constructor(inicio: int, fim: int) {
        this.inicio = inicio
        this.fim = fim
        this.atual = inicio
    }
    
    intent hasNext() -> bool {
        return this.atual < this.fim
    }
    
    intent next() -> int {
        if (not this.hasNext()) {
            return null
        }
        var valor = this.atual
        this.atual = this.atual + 1
        return valor
    }
}

class Intervalo implements Iterable<int> {
    var inicio: int
    var fim: int
    
    intent constructor(inicio: int, fim: int) {
        this.inicio = inicio
        this.fim = fim
    }
    
    intent __iter__() -> Iterator<int> {
        return new ContadorIterador(this.inicio, this.fim)
    }
}

intent main() {
    var intervalo = new Intervalo(1, 5)
    
    print("Iterando de 1 a 5:")
    for (var x in intervalo) {
        print("→", x)
    }
}

main()
```

**Use case:** Implementar ranges customizados, lazy evaluation.

---

## Exceções

### Capturar Exceções Tipadas

```mp
from core.lang.exceptions import GenericContractError

intent main() {
    try {
        // Simular erro de contrato genérico
        throw new GenericContractError("Tipo inválido na coleção")
    } catch (e: GenericContractError) {
        print("Erro capturado:", e.message)
        print("Tipo:", e.type)
        print("Stack:", e.stack)
    }
}

main()
```

---

### Multiple Exception Handling

```mp
intent main() {
    try {
        var x = 10 / 0  // Simulation
    } catch (e: ArithmeticException) {
        print("Erro aritmético:", e.message)
    } catch (e: NullPointerException) {
        print("Null pointer:", e.message)
    } catch (e: Exception) {
        print("Erro genérico:", e.message)
    } finally {
        print("Limpeza sempre executada")
    }
}

main()
```

---

## Data & Hora

### Operações Básicas com DateTime

```mp
intent main() {
    // Obter data de hoje
    var hoje = mf.datetime.today()
    print("Hoje:", hoje)
    
    // Criar data específica
    var natal = mf.datetime.date(2025, 12, 25)
    print("Natal 2025:", natal)
    
    // Hora atual
    var agora = mf.datetime.now()
    print("Agora:", agora)
    
    // Diferença entre datas
    var diferenca = natal.subtract(hoje)
    print("Dias até Natal:", diferenca.days)
}

main()
```

---

## String Operations

### Manipulação de Strings

```mp
intent main() {
    var texto = "Olá Mundo"
    
    print("Comprimento:", text.length(texto))         // 9
    print("Uppercase:", text.upper(texto))            // OLÁ MUNDO
    print("Lowercase:", text.lower(texto))            // olá mundo
    print("Contém 'Mundo'?", text.contains(texto, "Mundo"))  // true
    print("Substring:", text.substring(texto, 0, 3))  // Olá
    print("Replace:", text.replace(texto, "Mundo", "Python"))  // Olá Python
}

main()
```

---

### Split & Join

```mp
intent main() {
    var csv = "Alice,30,Engenheira"
    
    // Split
    var partes = text.split(csv, ",")
    print("Nome:", partes[0])      // Alice
    print("Idade:", partes[1])     // 30
    print("Cargo:", partes[2])     // Engenheira
    
    // Join
    var dados = ["Alice", "30", "Engenheira"]
    var reunido = text.join(dados, " | ")
    print("Reunido:", reunido)     // Alice | 30 | Engenheira
}

main()
```

---

## Null Safety

### Null-Friendly Operations

```mp
intent main() {
    var vazio = null
    
    // Concatenação com null é segura
    var mensagem = "Valor: " + vazio
    print(mensagem)         // Valor: null
    
    // Type checking
    print("Type de null:", type(vazio))  // null
    
    // Comparação
    if (vazio == null) {
        print("É realmente null")
    }
    
    // Operador elvis (se existir em Corplang)
    var valor_padrao = vazio ?: "padrão"
    print(valor_padrao)     // padrão
}

main()
```

---

## Demonstração Completa: Sistema de Produtos

Exemplo real integrando múltiplos conceitos:

```mp
from core.collections.list import List
from core.collections.map import Map

class Produto {
    var id: int
    var nome: string
    var preco: decimal
    
    intent constructor(id: int, nome: string, preco: decimal) {
        this.id = id
        this.nome = nome
        this.preco = preco
    }
    
    intent exibir() -> string {
        return "#" + this.id + ": " + this.nome + " - R$" + this.preco
    }
}

class Estoque {
    var produtos: List<Produto>
    var precos: Map<int, decimal>
    
    intent constructor() {
        this.produtos = new List<Produto>(null)
        this.precos = new Map<int, decimal>(null)
    }
    
    intent adicionar(produto: Produto) -> void {
        this.produtos.append(produto)
        this.precos.put(produto.id, produto.preco)
    }
    
    intent listar() -> void {
        print("=== Estoque ===")
        for (var p in this.produtos) {
            print(p.exibir())
        }
    }
    
    intent valor_total() -> decimal {
        var total = 0
        for (var p in this.produtos) {
            total = total + p.preco
        }
        return total
    }
}

intent main() {
    var estoque = new Estoque()
    
    estoque.adicionar(new Produto(1, "Notebook", 3500.00))
    estoque.adicionar(new Produto(2, "Mouse", 45.00))
    estoque.adicionar(new Produto(3, "Teclado", 150.00))
    
    estoque.listar()
    print("\nValor total:", estoque.valor_total())
}

main()
```

---

## Performance Tips

### Evitar Cópias Desnecessárias

```mp
from core.collections.list import List

intent main() {
    var grande_lista = new List<int>(null)
    
    // ✓ BOM: Iterar diretamente
    for (var item in grande_lista) {
        print(item)
    }
    
    // ✗ EVITAR: Copiar lista
    var copia = grande_lista  // Cria referência, não cópia
    // Para cópia real, use:
    // var copia = grande_lista.clone()
}

main()
```

---

## Referência Rápida

| Coleção | Operação | Uso |
|---------|----------|-----|
| List | append, get, remove | Sequência dinâmica |
| Map | put, get, keys, values | Dicionário |
| Set | add, remove, contains | Sem duplicatas |
| Stack | push, pop, peek | LIFO |
| Queue | enqueue, dequeue | FIFO |

---

## Próximas Etapas

1. **Agentes com Coleções**: Como usar List/Map em agentes?
   → [Tutorial 2 — Multi-Agent Routing](tutorials/02-multi-agent-routing.md)

2. **Genéricos Avançados**: Covariance e contravariance?
   → [Type System Reference](guides/type-system.md)

3. **Performance**: Qual coleção é mais rápida?
   → [Performance Guide](guides/performance.md)

---

**Dica:** Copie qualquer exemplo acima, salve em `exemplo.mp` e execute com `mf run exemplo.mp`.
