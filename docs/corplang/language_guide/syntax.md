# Guia de Sintaxe Corplang

A Corplang combina a legibilidade de Python com a estrutura robusta de linguagens como Java e TypeScript, adicionando comandos nativos para IA.

## Variáveis e Tipos

As variáveis são declaradas com a palavra-chave `var`. A Corplang suporta tipagem opcional e inferência de tipos.

```corplang
var nome = "Corplang"; // Inferência para string
var idade: int = 5;    // Tipagem explícita
```

### Tipos Primitivos
*   `int`, `float`, `string`, `bool`, `list`, `map`, `any`, `null`.

---

## Estruturas de Controle

### Condicionais (if/else)
Parênteses são opcionais na condição.

```corplang
if idade > 18 {
    print("Acesso permitido");
} else {
    print("Acesso negado");
}
```

### Loops (while e for)
Suporta o loop `while` tradicional e o `for` estilo C.

```corplang
var i = 0;
while i < 10 {
    print(i);
    i = i + 1;
}

for (var j = 0; j < 5; j = j + 1) {
    print("Contagem: {j}");
}
```

---

## Funções (Intents)

Na Corplang, funções são chamadas de `intents` (intenções), refletindo seu papel em sistemas de IA, mas também podem ser declaradas com `fn`.

```corplang
intent somar(a: int, b: int) -> int {
    return a + b;
}

// Funções assíncronas
async intent buscarDados() {
    var dados = await mf.net.fetch("http://api.exemplo.com");
    return dados;
}
```

---

## Comentários
*   `#` ou `//`: Comentários de linha única.
*   `/* ... */`: Comentários de múltiplas linhas.
*   `""" ... """`: Docstrings (documentação de módulos, classes e funções).

---

## Operadores Especiais
*   **Interpolação de String**: Use chaves `{}` dentro de strings prefixadas com `f` ou strings normais em contextos específicos.
*   **Operador `in`**: Verifica existência em coleções.
*   **Operador `delete`**: Remove propriedades ou índices.
