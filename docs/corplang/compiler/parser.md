# Parser (Analisador Sintático)

O `Parser` é o componente central responsável por transformar o fluxo de tokens gerado pelo Lexer em uma Árvore de Sintaxe Abstrata (AST). Ele foi projetado com uma arquitetura modular para facilitar a manutenção e a expansão da linguagem Corplang.

## Arquitetura Modular

O parser é dividido em um ponto de entrada principal e vários módulos especializados dentro do namespace `constants`:

*   **`src/corplang/compiler/parser.py`**: A classe `Parser` principal que orquestra o processo de parsing e conecta os sub-parsers especializados.
*   **`constants/core.py`**: Fornece o `TokenStream` para navegação e o `PositionTracker` para gerenciar o estado global e callbacks.
*   **`constants/expressions.py`**: Trata de todos os tipos de expressões (binárias, unárias, literais, chamadas, acessos a propriedades).
*   **`constants/statements.py`**: Lida com declarações de controle de fluxo como `if`, `while`, `for`, `return` e declarações de variáveis.
*   **`constants/declarations.py`**: Gerencia construções de alto nível como definições de `intent` (funções), `class`, `agent`, `interface` e `contract`.
*   **`constants/types.py`**: Responsável pelo parsing e formatação de anotações de tipo, incluindo suporte a genéricos.

## Funcionalidades de Destaque

*   **Rastreabilidade Obrigatória**: Cada nó gerado na AST inclui sua localização exata (`line`, `column`) e o caminho do arquivo de origem (`file_path`).
*   **Hierarquia de Nós (Parentesco)**: Os nós possuem um atributo `parent`, permitindo a navegação ascendente na AST, essencial para análises sensíveis ao contexto e relatórios de erro aprimorados.
*   **Recuperação de Erros**: O parser utiliza o `PositionTracker` para coletar múltiplos erros em uma única passagem sem interromper fatalmente a análise ao primeiro sinal de problema.
*   **Suporte a Palavras-chave como Identificadores**: Graças ao método `expect_identifier_like`, palavras-chave como `get`, `set` e `context` podem ser usadas como nomes de métodos ou variáveis sem causar erros de sintaxe.

## Exemplo de Uso

```python
from src.corplang.compiler.lexer import Lexer
from src.corplang.compiler.parser import Parser

code = "intent greet() { print('Olá Mundo'); }"
lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens, source_file="app.mp")
ast = parser.parse()

if parser.ctx.errors:
    for error in parser.ctx.errors:
        print(f"Erro Detectado: {error}")
```

## Estendendo a Linguagem

Para adicionar uma nova funcionalidade à Corplang:
1. Identifique o módulo apropriado (`expressions.py`, `statements.py`, etc.).
2. Implemente a nova função de parsing ou atualize uma existente.
3. Garanta que o novo nó herde de `ASTNode` em `nodes.py` e capture as informações de localização.
4. Registre o novo parser no método `_setup_context` da classe `Parser` se necessário.
