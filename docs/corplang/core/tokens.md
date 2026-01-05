# Tokens

Tokens are the smallest meaningful units of Corplang source code, produced by the Lexer for consumption by the Parser.

### TokenType

An enumeration of all recognized token categories in Corplang, including:

*   **Literals:** `NUMBER`, `STRING`, `BOOLEAN`, `NULL`, `FSTRING`.
*   **Keywords:** Control flow (`IF`, `FOR`), OOP (`CLASS`, `INTERFACE`), and specialized AI/Data keywords (`AGENT`, `MODEL`, `DATASET`).
*   **Operators:** Arithmetic (`PLUS`, `MINUS`), comparison (`EQUAL`, `LESS_THAN`), and logical (`AND`, `OR`).
*   **Delimiters:** Brackets, braces, parentheses, and punctuation.

### Token Structure

Each `Token` is an immutable data structure containing:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `type` | `TokenType` | The category of the token. |
| `value` | `str` | The raw text captured from the source. |
| `line` | `int` | The line number (1-based) where the token starts. |
| `column` | `int` | The column number (1-based) where the token starts. |

### Importance of Traceability

Mandatory `line` and `column` tracking on every token ensures that error messages can point exactly to the location of a syntax error or runtime issue, facilitating a better developer experience.
