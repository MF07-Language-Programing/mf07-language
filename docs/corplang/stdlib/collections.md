# Coleções (Collections)

As coleções na Corplang são projetadas para serem tipadas, seguras e eficientes. Elas suportam genéricos e oferecem interfaces claras para implementação de novas estruturas.

## List<T>

Localizada em `src/corplang/stdlib/core/collections/list.mp`, a `List<T>` é a principal estrutura de dados sequencial.

### Principais Características
*   **Genéricos**: Suporta a sintaxe `List<string>`, `List<int>`, etc.
*   **Validação de Tipo**: O método `append` verifica se o item corresponde ao tipo declarado na criação da lista.
*   **Inferência**: Se criada com valores iniciais e sem tipo explícito, a lista tenta inferir o tipo dos elementos.

### Exemplo de Uso
```corplang
var nomes = new List<string>(["Alice", "Bob"]);
nomes.append("Charlie"); // OK
nomes.append(10); // Gera um erro de tipo no console
```

---

## ImmutableList<T>

Localizada em `src/corplang/stdlib/core/collections/immutable_list.mp`, esta classe é ideal para programação funcional e cenários onde o estado não deve ser alterado.

### Comportamento
Qualquer operação que altere a lista retorna uma **nova instância** da lista com a alteração aplicada, preservando a original.

```corplang
var lista1 = new ImmutableList<int>([1, 2]);
var lista2 = lista1.append(3);

print(lista1.toList()); // [1, 2]
print(lista2.toList()); // [1, 2, 3]
```

---

## Interfaces Base

O módulo `icollection.mp` define o contrato para todas as coleções, permitindo polimorfismo e garantindo consistência.

### ICollection<T>
Define métodos fundamentais:
*   `size()`: Retorna a quantidade de elementos.
*   `isEmpty()`: Verifica se está vazia.
*   `clear()`: Remove todos os elementos.
*   `contains(value)`: Verifica a existência de um item.

### BaseCollection<T>
Uma classe abstrata que fornece implementações padrão para métodos comuns e suporte básico para ativação de IA (`enableAI()`).

---

## Algoritmos de Coleção

O módulo `algorithms.mp` fornece métodos estáticos úteis:
*   `Algorithms.sort(values)`: Ordena uma lista (usa o utilitário nativo).
*   `Algorithms.binary_search(values, target)`: Busca binária eficiente em listas ordenadas.
*   `Algorithms.shuffle(values)`: Embaralha os elementos aleatoriamente.
