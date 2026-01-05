# Lexer (Analisador Léxico)

O `Lexer` da Corplang é responsável por transformar o texto do código-fonte em uma corrente de objetos `Token`. Localizado em `src/corplang/compiler/lexer.py`, ele utiliza uma abordagem de varredura manual altamente otimizada, permitindo lidar com construções complexas que seriam difíceis de expressar apenas com expressões regulares.

## Características Principais

*   **Detecção Inteligente de JSON**: O Lexer possui uma funcionalidade única para detectar "blobs" JSON (`{...}` ou `[...]`) quando estes aparecem em contextos de atribuição ou parâmetros de agentes. Isso evita o overhead de processar cada elemento de um objeto de configuração como tokens individuais do parser.
*   **Suporte a F-Strings e Docstrings**: Suporta interpolação de strings e comentários de múltiplas linhas que são preservados na AST.
*   **Rastreabilidade Total**: Cada token inclui sua posição exata (linha e coluna) para relatórios de erro precisos.
*   **Reconhecimento de Palavras-chave**: Categoriza automaticamente identificadores que correspondem a palavras reservadas (como `intent`, `agent`, `serve`).

## API Pública

### `Lexer(text: str)`
Inicializa o lexer com o código-fonte.

### `tokenize() -> List[Token]`
Processa o texto completo e retorna uma lista de objetos `Token`, finalizando com um token `EOF`.

## Amostragem e Depuração (LexerSampler)

A classe `Lexer` herda de `LexerSampler`, que fornece métodos integrados para gerar relatórios legíveis por humanos do processo de tokenização. Isso é extremamente útil para verificação e depuração de gramática.

### Gerando Visualizações

```python
from src.corplang.compiler.lexer import Lexer

lexer = Lexer('var x = 10;')
# Gera relatório (tokeniza automaticamente se ainda não foi feito)
report = lexer.as_view()
print(report)

# Gera e salva em um arquivo
lexer.as_view(output_path="relatorio_lexer.txt")
```

### Formato do Relatório
O relatório inclui estatísticas de tokens e uma visualização anotada do código:
1. **Estatísticas**: Contagem de cada tipo de token encontrado.
2. **Stream Detalhada**: Lista cada token com seu valor e localização exata, correlacionando com a linha de código original.

## Lógica Interna
O Lexer utiliza uma abordagem de varredura de passo único com um mecanismo de lookahead (`_peek_char`). Ele ignora a maioria dos espaços em branco, mas gera tokens `NEWLINE` onde são significativos para a semântica da linguagem.
