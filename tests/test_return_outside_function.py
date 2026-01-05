from src.corplang.compiler import Lexer
from src.corplang.compiler.parser import Parser
from src.corplang.executor import execute
from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType


def _parse(source: str):
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize(), "<test>")
    return parser.parse()


def test_return_outside_function_is_syntax_error():
    ast = _parse("return 1")
    try:
        execute(ast)
        assert False, "Expected exception"
    except Exception as e:
        assert isinstance(e, CorpLangRuntimeError)
        assert e.error_type == RuntimeErrorType.SYNTAX_ERROR
        assert "Return statement outside" in str(e)


def test_return_inside_function_returns_value():
    ast = _parse("fn foo() { return 42 }\nfoo()")
    res = execute(ast)
    assert res == 42


def test_finally_return_overrides_try():
    ast = _parse("fn f() { try { return 1 } finally { return 2 } }\nf()")
    res = execute(ast)
    assert res == 2
