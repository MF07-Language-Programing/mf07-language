from typing import List, Optional, Callable, Any
from src.corplang.compiler.lexer import Token, TokenType


class SyntaxException(Exception):
    def __init__(self, line: int, column: int, position: int, expected: str, found: str):
        msg = (
            f"Syntax error at line {line}, column {column} (offset {position}): "
            f"expected {expected}, found {found}."
        )
        super().__init__(msg)
        self.line = line
        self.column = column
        self.position = position
        self.expected = expected
        self.found = found


class TokenStream:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
        self.pos = 0

    @property
    def current(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset: int = 1) -> Optional[Token]:
        idx = self.pos + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def advance(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            self.pos += 1
        return self.current

    def match(self, *types: TokenType) -> Optional[Token]:
        tok = self.current
        if tok and tok.type in types:
            self.advance()
            return tok
        return None

    def expect_identifier_like(self) -> Token:
        allowed = {
            TokenType.IDENTIFIER,
            TokenType.FN,
            TokenType.IMPORT,
            TokenType.DRIVER,
            TokenType.FROM,
            TokenType.AS,
            TokenType.IN,
            TokenType.OF,
            TokenType.TRAIN,
            TokenType.RUN,
            TokenType.PREDICT,
            TokenType.STOP,
            TokenType.ANALYZE,
            TokenType.USING,
            TokenType.PROVIDER,
            TokenType.CAPABILITY,
            TokenType.NULL,
            TokenType.CONTEXT,
            TokenType.STATIC,
            TokenType.ASYNC,
            TokenType.AWAIT,
            TokenType.PUBLIC,
            TokenType.PRIVATE,
            TokenType.PROTECTED,
            TokenType.DELETE,
            TokenType.GET,
            TokenType.SET,
        }
        tok = self.current
        if tok and tok.type in allowed:
            self.advance()
            return tok
        
        # Best-effort recovery: fabricate an identifier token
        fallback_value = tok.value if tok and tok.value else "__placeholder"
        fallback_token = Token(
            TokenType.IDENTIFIER, fallback_value, tok.line if tok else -1, tok.column if tok else -1
        )
        self.advance()
        return fallback_token

    def expect(self, *token_types: TokenType, expected: Optional[str] = None) -> Token:
        tok = self.current
        if tok and tok.type in token_types:
            self.advance()
            return tok
        
        if expected:
            expected_name = expected
        else:
            expected_name = " or ".join([t.name for t in token_types])
            
        found = tok.type.name if tok else "EOF"
        line = tok.line if tok else -1
        col = tok.column if tok else -1
        raise SyntaxException(line, col, self.pos, expected_name, found)

    def eof(self) -> bool:
        return self.current is None or self.current.type == TokenType.EOF


class PositionTracker:
    def __init__(self, stream: TokenStream, source_file: Optional[str] = None):
        self.stream = stream
        self.source_file = source_file
        self.errors: List[str] = []
        # callbacks wired in parser.py
        self.parse_expression: Callable[[Optional[Any]], Any] = lambda p=None: any
        self.parse_statement: Callable[[Optional[Any]], Any] = lambda p=None: any
        self.parse_type: Callable[[Optional[Any]], Any] = lambda p=None: any
        self.format_type: Callable[[Any], Optional[str]] = lambda ta: None

    def clone_position(self) -> int:
        return self.stream.pos

    def error(self, message: str):
        self.errors.append(message)


def parse_block(ctx: PositionTracker, parent: Optional[Any] = None) -> List[Any]:
    stream = ctx.stream
    stream.expect(TokenType.LBRACE)
    body: List[Any] = []
    while stream.current and stream.current.type != TokenType.RBRACE:
        if stream.current.type == TokenType.NEWLINE:
            stream.advance()
            continue
        start_pos = stream.pos
        try:
            stmt = ctx.parse_statement(parent)
            if stmt is not None:
                body.append(stmt)
        except Exception:
            # If an error occurs inside a block, we must advance to avoid infinite loop
            if stream.pos == start_pos:
                stream.advance()
            raise # Re-raise to be caught by top-level parser or caller

        # Safeguard against infinite loops if parse_statement returns None without advancing
        if stream.pos == start_pos and stream.current and stream.current.type != TokenType.RBRACE:
            stream.advance()
            
    stream.expect(TokenType.RBRACE)
    
    # Hoisting desativado: estava removendo declarações válidas em blocos comuns
    # parent_type = type(parent).__name__ if parent else None
    # if parent_type in ("FunctionDeclaration", "MethodDeclaration", "LambdaExpression"):
    #     from src.corplang.compiler.scope import BlockScopeHoister
    #     body = BlockScopeHoister.apply_hoisting(body, parent)
    
    return body


def separated(ctx: PositionTracker, parse_item: Callable[[], Any], separator: TokenType) -> List[Any]:
    items: List[Any] = []
    if ctx.stream.current is None:
        return items
    while True:
        items.append(parse_item())
        if ctx.stream.match(separator) is None:
            break
    return items
