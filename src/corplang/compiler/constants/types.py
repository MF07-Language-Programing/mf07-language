from typing import Optional, Any
from src.corplang.compiler.lexer import TokenType
from src.corplang.compiler.nodes import TypeAnnotation, GenericTypeExpression
from .core import PositionTracker, SyntaxException

def parse_type_annotation(ctx: PositionTracker, parent: Optional[Any] = None) -> TypeAnnotation:
    stream = ctx.stream
    tok = stream.current
    
    # Use expect_identifier_like to support keywords as types (e.g., Optional)
    type_tok = stream.expect_identifier_like()
    base = type_tok.value

    node = TypeAnnotation(
        base=base, 
        args=None, 
        line=tok.line, 
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    if stream.current and stream.current.type in (TokenType.LESS_THAN, TokenType.LBRACKET):
        start = stream.current.type
        closing = TokenType.GREATER_THAN if start == TokenType.LESS_THAN else TokenType.RBRACKET
        stream.advance()
        args = []
        while True:
            arg = parse_type_annotation(ctx, node)
            args.append(arg)
            if stream.match(TokenType.COMMA):
                continue
            break
        stream.expect(closing)
        node.args = args
        
        # If it has args, it could be a GenericTypeExpression in some contexts, 
        # but TypeAnnotation covers it. 

    # Support union types using '|' operator (e.g., int|float|str or Union<int,float>)
    if stream.current and stream.current.type == TokenType.OR:
        parts = [node]
        while stream.match(TokenType.OR):
            part = parse_type_annotation(ctx, parent)
            parts.append(part)
        # Represent unions using base 'Union' and args as the variant types
        union = TypeAnnotation(base="Union", args=parts, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        return union

    return node


def format_type_annotation(ta: Optional[TypeAnnotation]) -> Optional[str]:
    if ta is None:
        return None
    if not ta.args:
        return ta.base
    # Pretty-print unions using '|' for readability
    if ta.base == "Union":
        return "|".join(filter(None, (format_type_annotation(a) for a in ta.args)))
    return (
        f"{ta.base}<" + ", ".join(filter(None, (format_type_annotation(a) for a in ta.args))) + ">"
    )
