from src.corplang.compiler.lexer import Lexer
from src.corplang.compiler.parser import Parser
from src.corplang.compiler.constants.types import format_type_annotation


def parse_type(src: str):
    tokens = Lexer(src).tokenize()
    p = Parser(tokens, source_file="<test>")
    # use ctx.parse_type directly
    ta = p.ctx.parse_type()
    return ta


def test_union_pipe_syntax():
    ta = parse_type("int|float")
    assert format_type_annotation(ta) == "int|float"


def test_union_explicit_syntax():
    ta = parse_type("Union<int, string>")
    assert format_type_annotation(ta) == "int|string"
