from typing import List
from src.corplang.compiler.lexer import Token, TokenType


def normalize(tokens: List[Token]) -> List[Token]:
    return [t for t in tokens if t.type != TokenType.NEWLINE]
