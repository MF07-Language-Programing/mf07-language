# Compilador Corplang: Visão Geral

O compilador Corplang é uma ferramenta robusta projetada para transformar o código-fonte da linguagem Corplang (arquivos `.mp` e `.mf`) em uma Árvore de Sintaxe Abstrata (AST) rastreável e processável. Ele foca em três pilares: **Rastreabilidade**, **Modularidade** e **Suporte Nativo a IA**.

## Fluxo de Compilação

O processo de compilação segue um pipeline clássico, mas altamente otimizado para as necessidades da Corplang:

1.  **Lexing (Análise Léxica)**: O `Lexer` converte o texto bruto em uma sequência de tokens significativos.
2.  **Parsing (Análise Sintática)**: O `Parser` organiza os tokens em uma estrutura hierárquica (AST).
3.  **Tratamento de Contexto**: Durante o parsing, metadados como localização (linha/coluna) e relações de parentesco entre nós são preservados para análise posterior.

## Componentes Principais

### [Lexer](./lexer.md)
Responsável por identificar palavras-chave, operadores, literais e estruturas complexas como blobs JSON incorporados diretamente no código.

### [Parser](./parser.md)
Uma implementação modular que divide a responsabilidade de interpretar diferentes partes da linguagem:
*   **Declarações**: Classes, Agentes, Funções, Interfaces e Contratos.
*   **Statements**: Controle de fluxo (if, while, for), variáveis e comandos especializados (serve, loop).
*   **Expressões**: Operações matemáticas, chamadas de função, acessos a propriedades e literais de IA.

### [Nós da AST (Nodes)](./ast_nodes.md)
Define a estrutura de dados que representa o programa. Cada nó é uma `dataclass` Python que contém todas as informações necessárias para execução ou transpilação.

## Filosofia de Design

*   **Rastreabilidade Total**: Todo erro gerado aponta exatamente para o arquivo, linha e coluna de origem.
*   **IA de Primeira Classe**: A sintaxe para Agentes e modelos de linguagem não é um "add-on", mas parte integrante do núcleo do parser.
*   **Flexibilidade**: O uso de `expect_identifier_like` permite que a linguagem evolua sem que palavras-chave comuns causem quebras em nomes de métodos ou variáveis na `stdlib`.

---
*Este documento faz parte da documentação técnica do projeto MF07 Corplang.*
