# Sistema e Tipos Base

Este módulo fornece acesso a recursos do sistema operacional e estende as capacidades numéricas da linguagem.

## Variáveis de Ambiente (Env)

Localizada em `src/corplang/stdlib/core/system/env.mp`, a classe `Env` permite interagir com as configurações do ambiente de execução de forma segura.

### Métodos
*   **`static intent get(key: string, defaultValue = null)`**: Recupera o valor de uma variável de ambiente. Se a chave não existir ou ocorrer um erro, retorna o valor padrão.
*   **`static intent set(key: string, value: string)`**: Define o valor de uma variável de ambiente.
*   **`static intent has(key: string): bool`**: Verifica a existência de uma chave no ambiente.

### Exemplo
```corplang
var db_url = Env.get("DATABASE_URL", "http://localhost:5432");
if (Env.has("DEBUG_MODE")) {
    print("Modo debug ativado");
}
```

---

## BigInt (Inteiros Longos)

Localizada em `src/corplang/stdlib/core/base/bigint.mp`, a classe `BigInt` oferece suporte para operações matemáticas que excedem o limite dos tipos inteiros padrão de 64 bits.

### Operações Suportadas
A classe `BigInt` encapsula chamadas nativas (`mf.math.bigint`) e permite operações aritméticas básicas através de métodos estáticos:
*   `BigInt.add(a, b)`
*   `BigInt.sub(a, b)`
*   `BigInt.mul(a, b)`

### Conversão
O método `BigInt.from(value)` é resiliente e tenta converter strings ou números para o formato `BigInt`, retornando `0` em caso de falha crítica.

```corplang
var a = BigInt.from("9007199254740991000");
var b = BigInt.from(1000);
var resultado = BigInt.add(a, b);
```
