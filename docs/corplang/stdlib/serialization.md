# Serialização e Texto

A Corplang oferece ferramentas integradas para manipulação de formatos de dados comuns no mundo corporativo e um motor de templates simples.

## JSON e YAML

A biblioteca padrão fornece wrappers sobre as funcionalidades nativas da Meta-Framework para garantir uma interface consistente.

*   **JSON**: Suporte para `parse` e `stringify` de objetos e arrays.
*   **YAML**: Leitura de arquivos de configuração complexos.

## Templates

Localizado em `src/corplang/stdlib/core/text/template.mp`, o módulo `Template` permite a expansão dinâmica de strings usando um sistema de tags `{{key}}`.

### Renderização
O método `render` aceita uma string de template e um objeto/mapa de contexto.

```corplang
var texto = "Olá {{usuario}}, seu saldo é {{saldo}}.";
var contexto = { "usuario": "Carlos", "saldo": 1500.50 };

var final = Template.render(texto, contexto);
print(final); // "Olá Carlos, seu saldo é 1500.5."
```

### Características
*   **Resiliência**: Se o template for nulo, retorna uma string vazia. Se o contexto for nulo, retorna o template original sem alterações.
*   **Conversão Automática**: Chama o método `toString()` de cada valor no contexto antes de realizar a substituição.

---

## Formatação e Utilidades

A Corplang também inclui utilitários para:
*   **Strings**: Manipulação de capitalização, recortes e buscas.
*   **Loggers**: Sistemas de log com diferentes níveis (INFO, WARN, ERROR) integrados ao console e arquivos.
