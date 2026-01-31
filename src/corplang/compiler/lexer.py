import json
from typing import List, Optional, Dict, Tuple

from src.corplang.core.config import get_logger
from src.corplang.core.tokens import TokenType, Token
from src.corplang.compiler.sampler import LexerSampler


class Lexer(LexerSampler):
    """
    Highly optimized and modular Lexer for the Corplang language.
    Responsible for converting source code into a stream of Tokens.
    """

    KEYWORDS: Dict[str, TokenType] = {
        "var": TokenType.VAR,
        "intent": TokenType.FUNCTION,
        "fn": TokenType.FN,
        "async": TokenType.ASYNC,
        "await": TokenType.AWAIT,
        "class": TokenType.CLASS,
        "extends": TokenType.EXTENDS,
        "implements": TokenType.IMPLEMENTS,
        "interface": TokenType.INTERFACE,
        "abstract": TokenType.ABSTRACT,
        "static": TokenType.STATIC,
        "private": TokenType.PRIVATE,
        "public": TokenType.PUBLIC,
        "protected": TokenType.PROTECTED,
        "contract": TokenType.CONTRACT,
        "driver": TokenType.DRIVER,
        "protocol": TokenType.PROTOCOL,
        "new": TokenType.NEW,
        "this": TokenType.THIS,
        "super": TokenType.SUPER,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "for": TokenType.FOR,
        "in": TokenType.IN,
        "of": TokenType.OF,
        "return": TokenType.RETURN,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE,
        "true": TokenType.BOOLEAN,
        "false": TokenType.BOOLEAN,
        "null": TokenType.NULL,
        "None": TokenType.NULL,
        "and": TokenType.AND,
        "or": TokenType.OR,
        "not": TokenType.NOT,
        "dataset": TokenType.DATASET,
        "enum": TokenType.ENUM,
        "model": TokenType.MODEL,
        "predict": TokenType.PREDICT,
        "train": TokenType.TRAIN,
        "analyze": TokenType.ANALYZE,
        "migration": TokenType.MIGRATION,
        "import": TokenType.IMPORT,
        "from": TokenType.FROM,
        "as": TokenType.AS,
        "try": TokenType.TRY,
        "catch": TokenType.CATCH,
        "finally": TokenType.FINALLY,
        "throw": TokenType.THROW,
        "with": TokenType.WITH,
        "agent": TokenType.AGENT,
        "run": TokenType.RUN,
        "intelligence": TokenType.INTELLIGENCE,
        "context": TokenType.CONTEXT,
        "execution": TokenType.EXECUTION,
        "allow": TokenType.ALLOW,
        "deny": TokenType.DENY,
        "provider": TokenType.PROVIDER,
        "capability": TokenType.CAPABILITY,
        "hallucination": TokenType.HALLUCINATION,
        "loop": TokenType.LOOP,
        "using": TokenType.USING,
        "serve": TokenType.SERVE,
        "stop": TokenType.STOP,
        "delete": TokenType.DELETE,
        "get": TokenType.GET,
        "set": TokenType.SET,
        "authentication": TokenType.AUTHENTICATION,
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.logger = get_logger(__name__)

    def _current_char(self) -> Optional[str]:
        """Returns the character at current position or None if at EOF."""
        return self.text[self.pos] if self.pos < len(self.text) else None

    def _peek_char(self, offset: int = 1) -> Optional[str]:
        """Peeks ahead in the text by a given offset."""
        peek_pos = self.pos + offset
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def _advance(self):
        """Advances the position and updates line/column counters."""
        self.pos += 1
        if self.text[self.pos-1] == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

    def _add_token(self, token_type: TokenType, value: str, line: Optional[int] = None, col: Optional[int] = None):
        """Helper to append a new token to the list."""
        self.tokens.append(Token(
            type=token_type,
            value=value,
            line=line if line is not None else self.line,
            column=col if col is not None else self.column
        ))

    def _last_significant_char(self) -> str:
        """Returns the last non-whitespace character before the current position."""
        i = self.pos - 1
        while i >= 0 and self.text[i] in " \t\r\n":
            i -= 1
        return self.text[i] if i >= 0 else ""

    def _skip_whitespace(self):
        """Consumes spaces, tabs, and carriage returns."""
        while char := self._current_char():
            if char in " \t\r":
                self._advance()
            else:
                break

    def _scan_comment(self) -> bool:
        """Handles single-line (# or //) and multi-line (/* */) comments."""
        char = self._current_char()
        if char == "#":
            while self._current_char() and self._current_char() != "\n":
                self._advance()
            return True

        if char == "/" and self._peek_char() == "/":
            self._advance()  # /
            self._advance()  # /
            while self._current_char() and self._current_char() != "\n":
                self._advance()
            return True

        if char == "/" and self._peek_char() == "*":
            self._advance()  # /
            self._advance()  # *
            while True:
                curr = self._current_char()
                if curr is None:
                    break
                if curr == "*" and self._peek_char() == "/":
                    self._advance()  # *
                    self._advance()  # /
                    break
                self._advance()
            return True

        return False

    def _scan_json_blob(self) -> bool:
        """Detects and reads JSON-like structures for objects and arrays."""
        char = self._current_char()
        if char not in ("{", "["):
            return False

        # Only attempt to parse as JSON if it's in an expression-like context
        prev = self._last_significant_char()
        
        # In Corplang, [0] or [1:2] can be index access.
        # If it follows an identifier or closing bracket/quote, it's likely 
        # an index access or block, NOT a JSON literal.
        if prev and (prev.isalnum() or prev in ("}", "]", ")", "\"", "'", "_")):
             # If it's '[', and follows an identifier/bracket, it's IndexAccess.
             # We should NOT scan it as a JSON blob.
             if char == "[":
                 return False
             # If it's '{' and follows an identifier, it might be a block or object literal.
             # Blocks usually don't have colons right away.
             if char == "{":
                 # Heuristic: if it's an object literal, it usually contains a colon.
                 # But Lexer doesn't know context. 
                 # Let's be conservative and only allow JSON blobs after certain operators.
                 if prev not in (":", "=", "(", "[", ","):
                     return False

        start_pos, start_line, start_col = self.pos, self.line, self.column
        try:
            json_str = self._read_balanced_structure(char)
            json.loads(json_str)
            token_type = TokenType.OBJECT if char == "{" else TokenType.ARRAY
            self._add_token(token_type, json_str, start_line, start_col)
            return True
        except (SyntaxError, json.JSONDecodeError):
            # Rollback and let regular tokenization handle it
            self.pos, self.line, self.column = start_pos, start_line, start_col
            return False

    def _read_balanced_structure(self, start_char: str) -> str:
        """Reads a balanced bracket/brace structure."""
        matching = {"{": "}", "[": "]"}
        end_char = matching[start_char]
        bracket_count = 0
        result = ""
        in_string = False
        current_quote = None
        escape_next = False

        while char := self._current_char():
            # Security validation
            if not in_string and not char.isprintable() and char not in ("\n", "\r", "\t"):
                 raise SyntaxError(f"Invalid character in structure: {repr(char)}")

            result += char
            
            if not escape_next and char in ('"', "'"):
                if not in_string:
                    in_string, current_quote = True, char
                elif char == current_quote:
                    in_string, current_quote = False, None
            
            if in_string and char == "\\" and not escape_next:
                escape_next = True
            else:
                escape_next = False

            if not in_string:
                if char == start_char:
                    bracket_count += 1
                elif char == end_char:
                    bracket_count -= 1

            self._advance()
            if bracket_count == 0 and not in_string:
                break
        
        if bracket_count != 0:
            raise SyntaxError(f"Unbalanced structure: expected matching '{end_char}'")
        return result

    def _scan_number(self):
        """Reads numeric literals (integers and floats)."""
        start_line, start_col = self.line, self.column
        num_str = ""
        while char := self._current_char():
            if char.isdigit() or char == ".":
                num_str += char
                self._advance()
            else:
                break
        self._add_token(TokenType.NUMBER, num_str, start_line, start_col)

    def _scan_fstring(self):
        """Handles f-strings by capturing the 'f' prefix and the string content."""
        start_line, start_col = self.line, self.column
        self._advance()  # Consume 'f'
        self._scan_string(is_fstring=True, start_pos=(start_line, start_col))

    def _scan_string(self, is_fstring: bool = False, start_pos: Optional[Tuple[int, int]] = None):
        """Reads single and triple quoted strings."""
        s_line, s_col = start_pos if start_pos else (self.line, self.column)
        quote_char = self._current_char()
        
        is_triple = False
        if self._peek_char(1) == quote_char and self._peek_char(2) == quote_char:
            is_triple = True
            for _ in range(3): self._advance()
        else:
            self._advance()

        content = ""
        while True:
            char = self._current_char()
            if char is None:
                break
            
            if is_triple:
                if char == quote_char and self._peek_char(1) == quote_char and self._peek_char(2) == quote_char:
                    for _ in range(3): self._advance()
                    break
            elif char == quote_char:
                self._advance()
                break
            
            if char == "\\" and not is_triple:
                self._advance()
                esc = self._current_char()
                mapping = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", quote_char: quote_char}
                content += mapping.get(esc, esc) if esc else ""
            else:
                content += char
            
            self._advance()

        token_type = TokenType.FSTRING if is_fstring else (TokenType.DOCSTRING if is_triple else TokenType.STRING)
        self._add_token(token_type, content, s_line, s_col)

    def _scan_identifier(self):
        """Reads identifiers and keywords."""
        start_line, start_col = self.line, self.column
        name = ""
        while char := self._current_char():
            if char.isalnum() or char == "_":
                name += char
                self._advance()
            else:
                break
        
        token_type = self.KEYWORDS.get(name, TokenType.IDENTIFIER)
        self._add_token(token_type, name, start_line, start_col)

    def _scan_operator(self):
        """Handles operators and multi-character delimiters."""
        char = self._current_char()
        line, col = self.line, self.column
        next_char = self._peek_char()

        # Two-character operators
        pairs = {
            "==": TokenType.EQUAL,
            "!=": TokenType.NOT_EQUAL,
            "<=": TokenType.LESS_EQUAL,
            ">=": TokenType.GREATER_EQUAL,
        }
        
        if next_char and (char + next_char) in pairs:
            self._add_token(pairs[char + next_char], char + next_char, line, col)
            self._advance()
            self._advance()
            return

        # Single-character operators
        singles = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "%": TokenType.MODULO,
            "=": TokenType.ASSIGN,
            "!": TokenType.NOT,
            "<": TokenType.LESS_THAN,
            ">": TokenType.GREATER_THAN,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ";": TokenType.SEMICOLON,
            ":": TokenType.COLON,
            "?": TokenType.QUESTION,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            "|": TokenType.OR, # Just in case some file uses |
            "&": TokenType.AND, # Just in case
        }

        if char in singles:
            self._add_token(singles[char], char, line, col)
            self._advance()
        else:
            raise SyntaxError(f"Unexpected character '{char}' at line {line}, col {col}")

    def tokenize(self) -> List[Token]:
        """
        Processes the input text and returns a list of tokens.
        """
        while char := self._current_char():
            if char in " \t\r":
                self._skip_whitespace()
            elif char == "\n":
                self._add_token(TokenType.NEWLINE, "\n")
                self._advance()
            elif char in ("#", "/"):
                if not self._scan_comment():
                    self._scan_operator()
            elif char in ("{", "["):
                if not self._scan_json_blob():
                    self._scan_operator()
            elif (char in ("f", "F")) and (self._peek_char() in ("'", '"')):
                self._scan_fstring()
            elif char.isdigit():
                self._scan_number()
            elif char in ("'", '"'):
                self._scan_string()
            elif char.isalpha() or char == "_":
                self._scan_identifier()
            else:
                self._scan_operator()

        self._add_token(TokenType.EOF, "", self.line, self.column)
        return self.tokens


__all__ = ["TokenType", "Token", "Lexer"]
