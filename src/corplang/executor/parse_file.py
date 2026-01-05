"""Minimal parse_file utility for executor/*, similar to execute()."""
from src.corplang.compiler.lexer import Lexer
from src.corplang.compiler.parser import Parser

def parse_file(path: str):
    """Parse a .mp file and return the AST root node."""
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    lexer = Lexer(source)
    parser = Parser(lexer)
    return parser.parse()
