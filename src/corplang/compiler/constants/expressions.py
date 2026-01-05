from typing import Any, List, Optional
from src.corplang.compiler.lexer import TokenType
from src.corplang.compiler.nodes import (
    Literal, Identifier, BinaryOp, UnaryOp, FunctionCall, CallArgument,
    PropertyAccess, IndexAccess, NewExpression, ThisExpression, SuperExpression,
    LambdaExpression, Ternary, InterpolatedString, JsonObject, JsonArray, NullLiteral,
    Assignment, Await, AwaitStatement, GenericIdentifier
)
from .core import PositionTracker, separated


def parse_expression(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    tok = ctx.stream.current
    if tok and tok.type == TokenType.AWAIT:
        return parse_await(ctx, parent)
    return parse_assignment(ctx, parent)


def parse_await(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    tok = ctx.stream.expect(TokenType.AWAIT)
    # Check if it's a statement level await (simple identifier) or expression
    if ctx.stream.current and ctx.stream.current.type == TokenType.IDENTIFIER and (
            ctx.stream.peek() is None or ctx.stream.peek().type == TokenType.SEMICOLON):
        target = ctx.stream.advance().value
        node = AwaitStatement(target=target, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        ctx.stream.match(TokenType.SEMICOLON)
        return node

    expr = parse_expression(ctx)
    node = Await(expression=expr, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
    if hasattr(expr, 'parent'):
        expr.parent = node
    return node


def parse_assignment(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    target = parse_ternary(ctx, parent)
    if ctx.stream.match(TokenType.ASSIGN):
        node = Assignment(
            target=target,
            value=None,  # To be filled
            line=target.line,
            column=target.column,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(target, 'parent'):
            target.parent = node

        value = parse_expression(ctx, node)
        node.value = value
        return node
    return target


def parse_ternary(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    condition = parse_or(ctx, parent)
    if ctx.stream.match(TokenType.QUESTION):
        node = Ternary(
            condition=condition,
            true_expr=None,
            false_expr=None,
            line=condition.line if condition else ctx.stream.pos,
            column=condition.column if condition else 0,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(condition, 'parent'):
            condition.parent = node

        node.true_expr = parse_expression(ctx, node)
        ctx.stream.expect(TokenType.COLON)
        node.false_expr = parse_expression(ctx, node)
        return node
    return condition


def parse_or(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    left = parse_and(ctx, parent)
    while tok := ctx.stream.match(TokenType.OR):
        node = BinaryOp(
            left=left,
            operator="or",
            right=None,
            line=tok.line,
            column=tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(left, 'parent'):
            left.parent = node

        right = parse_and(ctx, node)
        node.right = right
        left = node
    return left


def parse_and(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    left = parse_equality(ctx, parent)
    while tok := ctx.stream.match(TokenType.AND):
        node = BinaryOp(
            left=left,
            operator="and",
            right=None,
            line=tok.line,
            column=tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(left, 'parent'):
            left.parent = node

        right = parse_equality(ctx, node)
        node.right = right
        left = node
    return left


def parse_equality(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    left = parse_comparison(ctx, parent)
    while tok := ctx.stream.match(TokenType.EQUAL, TokenType.NOT_EQUAL):
        node = BinaryOp(
            left=left,
            operator=tok.value,
            right=None,
            line=tok.line,
            column=tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(left, 'parent'):
            left.parent = node

        right = parse_comparison(ctx, node)
        node.right = right
        left = node
    return left


def parse_comparison(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    left = parse_additive(ctx, parent)
    while tok := ctx.stream.match(
            TokenType.LESS_THAN, TokenType.GREATER_THAN,
            TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
            TokenType.IN
    ):
        node = BinaryOp(
            left=left,
            operator=tok.value,
            right=None,
            line=tok.line,
            column=tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(left, 'parent'):
            left.parent = node

        right = parse_additive(ctx, node)
        node.right = right
        left = node
    return left


def parse_additive(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    left = parse_multiplicative(ctx, parent)
    while tok := ctx.stream.match(TokenType.PLUS, TokenType.MINUS):
        node = BinaryOp(
            left=left,
            operator=tok.value,
            right=None,
            line=tok.line,
            column=tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(left, 'parent'):
            left.parent = node

        right = parse_multiplicative(ctx, node)
        node.right = right
        left = node
    return left


def parse_multiplicative(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    left = parse_unary(ctx, parent)
    while tok := ctx.stream.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
        node = BinaryOp(
            left=left,
            operator=tok.value,
            right=None,
            line=tok.line,
            column=tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        if hasattr(left, 'parent'):
            left.parent = node

        right = parse_unary(ctx, node)
        node.right = right
        left = node
    return left


def parse_unary(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    if tok := ctx.stream.match(TokenType.MINUS, TokenType.NOT):
        node = UnaryOp(
            operator=tok.value,
            operand=None,
            line=tok.line,
            column=tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        node.operand = parse_unary(ctx, node)
        return node
    return parse_primary(ctx, parent)


def parse_lambda_expression(ctx: PositionTracker, parent: Optional[Any] = None) -> LambdaExpression:
    stream = ctx.stream
    tok = stream.expect(TokenType.FN)

    params = []
    param_types = {}
    param_defaults = {}

    if stream.match(TokenType.LPAREN):
        if stream.current.type != TokenType.RPAREN:
            while True:
                p_name = stream.expect(TokenType.IDENTIFIER).value
                params.append(p_name)
                if stream.match(TokenType.COLON):
                    param_types[p_name] = ctx.format_type(ctx.parse_type())
                if stream.match(TokenType.ASSIGN):
                    param_defaults[p_name] = parse_expression(ctx)
                if not stream.match(TokenType.COMMA):
                    break
        stream.expect(TokenType.RPAREN)

    return_type = None
    if stream.match(TokenType.COLON):
        return_type = ctx.format_type(ctx.parse_type())

    node = LambdaExpression(
        params=params,
        param_types=param_types,
        param_defaults=param_defaults,
        return_type=return_type,
        body=[],
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )

    # Lambda body can be an expression or a block
    if stream.current and stream.current.type == TokenType.LBRACE:
        from .core import parse_block
        node.body = parse_block(ctx, node)
    else:
        expr = parse_expression(ctx, node)
        node.body = [expr]

    return node


def parse_primary(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    stream = ctx.stream
    tok = stream.current
    if not tok:
        return None

    node = None
    if tok.type == TokenType.NUMBER:
        val = float(tok.value) if "." in tok.value else int(tok.value)
        node = Literal(value=val, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        stream.advance()
    elif tok.type == TokenType.STRING:
        node = Literal(value=tok.value, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        stream.advance()
    elif tok.type == TokenType.BOOLEAN:
        node = Literal(value=(tok.value == "true"), line=tok.line, column=tok.column, file_path=ctx.source_file,
                       parent=parent)
        stream.advance()
    elif tok.type == TokenType.NULL:
        node = NullLiteral(line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        stream.advance()
    elif tok.type == TokenType.FN:
        node = parse_lambda_expression(ctx, parent)
    elif tok.type in (
        TokenType.IDENTIFIER, TokenType.FN, TokenType.IMPORT, TokenType.DRIVER, TokenType.FROM,
        TokenType.AS, TokenType.IN, TokenType.OF, TokenType.TRAIN, TokenType.RUN, TokenType.PREDICT,
        TokenType.STOP, TokenType.ANALYZE, TokenType.USING, TokenType.PROVIDER, TokenType.CAPABILITY,
        TokenType.CONTEXT, TokenType.STATIC, TokenType.ASYNC, TokenType.AWAIT, TokenType.PUBLIC,
        TokenType.PRIVATE, TokenType.PROTECTED, TokenType.DELETE, TokenType.GET, TokenType.SET
    ):
        # Check if it's a GenericIdentifier: identifier<T>
        # We need a heuristic or lookahead because '<' is also 'LESS_THAN'
        is_generic = False
        if stream.peek() and stream.peek().type == TokenType.LESS_THAN:
            # Look ahead to see if there's a matching '>' before certain delimiters
            # like '(', '{', ';', '}', ']', ')'
            lookahead = 2
            found_gt = False
            while True:
                next_tok = stream.peek(lookahead)
                if not next_tok or next_tok.type in (
                        TokenType.SEMICOLON, TokenType.LBRACE, TokenType.RBRACE,
                        TokenType.RPAREN, TokenType.LPAREN, TokenType.ASSIGN
                ):
                    break
                if next_tok.type == TokenType.GREATER_THAN:
                    found_gt = True
                    break
                lookahead += 1

            if found_gt:
                is_generic = True

        if is_generic:
            name_tok = stream.expect_identifier_like()
            stream.expect(TokenType.LESS_THAN)
            args = []
            while True:
                args.append(ctx.parse_type())
                if not stream.match(TokenType.COMMA): break
            stream.expect(TokenType.GREATER_THAN)
            node = GenericIdentifier(name=name_tok.value, generic_args=args, line=name_tok.line, column=name_tok.column,
                                     file_path=ctx.source_file, parent=parent)
        else:
            node = Identifier(name=tok.value, line=tok.line, column=tok.column, file_path=ctx.source_file,
                              parent=parent)
            stream.advance()
    elif tok.type == TokenType.OBJECT:
        node = JsonObject(value={}, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        # Em um interpretador real, aqui parsearíamos o valor do token string para um dict
        import json
        try:
            node.value = json.loads(tok.value)
        except:
            pass
        stream.advance()
    elif tok.type == TokenType.ARRAY:
        node = JsonArray(value=[], line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        import json
        try:
            node.value = json.loads(tok.value)
        except:
            pass
        stream.advance()
    elif tok.type == TokenType.FSTRING:
        # Parse f-string content into static parts and expression nodes so runtime
        # can evaluate placeholders (e.g., f"Hi {this.nome}"). Support escaping
        # with {{ and }} to include literal braces.
        content = tok.value or ""
        parts: list = []
        i = 0
        while i < len(content):
            ch = content[i]
            if ch == "{" and i + 1 < len(content) and content[i+1] == "{":
                parts.append("{")
                i += 2
                continue
            if ch == "}" and i + 1 < len(content) and content[i+1] == "}":
                parts.append("}")
                i += 2
                continue
            if ch == "{":
                # find matching '}' (non-nested)
                j = i + 1
                while j < len(content) and content[j] != "}":
                    j += 1
                if j >= len(content):
                    # unmatched brace: treat as literal
                    parts.append(content[i:])
                    break
                expr_text = content[i+1:j].strip()
                # parse inner expression using parser on the substring
                try:
                    from src.corplang.compiler.lexer import Lexer as _Lexer
                    from src.corplang.compiler.parser import Parser as _Parser

                    inner_tokens = _Lexer(expr_text).tokenize()
                    inner_parser = _Parser(inner_tokens, source_file=ctx.source_file)
                    expr_node = inner_parser.ctx.parse_expression()
                    parts.append(expr_node)
                except Exception:
                    # If parsing fails, keep the raw text inside braces
                    parts.append("{" + expr_text + "}")
                i = j + 1
                continue
            # accumulate static text until next brace
            j = i
            while j < len(content) and content[j] not in "{}":
                j += 1
            parts.append(content[i:j])
            i = j
        node = InterpolatedString(parts=parts, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        stream.advance()
    elif tok.type == TokenType.LBRACKET:
        # Array literal
        node = parse_array_literal(ctx, parent)
    elif tok.type == TokenType.LBRACE:
        # Object literal
        node = parse_object_literal(ctx, parent)
    elif tok.type == TokenType.NEW:
        new_tok = stream.current
        stream.advance()
        
        # Parse base class name
        class_name_tok = stream.expect_identifier_like()
        class_name = class_name_tok.value
        
        # Parse optional type arguments: new List<int>()
        type_arguments = None
        if stream.current and stream.current.type == TokenType.LESS_THAN:
            stream.advance()
            type_arguments = []
            while True:
                type_arg = ctx.parse_type()
                type_arguments.append(type_arg)
                if stream.match(TokenType.COMMA):
                    continue
                break
            stream.expect(TokenType.GREATER_THAN)
        
        stream.expect(TokenType.LPAREN)
        node = NewExpression(
            class_name=class_name,
            type_arguments=type_arguments,
            args=[],
            line=new_tok.line,
            column=new_tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        node.args = parse_call_arguments(ctx, node)
    elif tok.type == TokenType.THIS:
        node = ThisExpression(line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        stream.advance()
    elif tok.type == TokenType.SUPER:
        node = SuperExpression(line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
        stream.advance()
    elif tok.type == TokenType.LPAREN:
        stream.advance()
        node = parse_expression(ctx, parent)
        stream.expect(TokenType.RPAREN)

    if node:
        return parse_access_and_call(ctx, node)

    return None


def parse_access_and_call(ctx: PositionTracker, node: Any) -> Any:
    stream = ctx.stream
    while True:
        if stream.match(TokenType.DOT):
            prop_tok = stream.expect_identifier_like()
            new_node = PropertyAccess(
                obj=node,
                prop=prop_tok.value,
                line=node.line,
                column=node.column,
                file_path=ctx.source_file,
                parent=node.parent
            )
            if hasattr(node, 'parent'):
                node.parent = new_node
            node = new_node
        elif stream.match(TokenType.LBRACKET):
            index = parse_expression(ctx)
            stream.expect(TokenType.RBRACKET)
            new_node = IndexAccess(
                obj=node,
                index=index,
                line=node.line,
                column=node.column,
                file_path=ctx.source_file,
                parent=node.parent
            )
            if hasattr(node, 'parent'):
                node.parent = new_node
            if hasattr(index, 'parent'):
                index.parent = new_node
            node = new_node
        elif stream.match(TokenType.LPAREN):
            new_node = FunctionCall(
                callee=node,
                args=[],
                line=node.line,
                column=node.column,
                file_path=ctx.source_file,
                parent=node.parent
            )
            if hasattr(node, 'parent'):
                node.parent = new_node
            new_node.args = parse_call_arguments(ctx, new_node)
            node = new_node
        else:
            break
    return node


def parse_call_arguments(ctx: PositionTracker, parent: Optional[Any] = None) -> List[CallArgument]:
    args: List[CallArgument] = []
    if ctx.stream.current and ctx.stream.current.type != TokenType.RPAREN:
        while True:
            name = None
            # Use a lookahead for named arguments
            if ctx.stream.current.type in (TokenType.IDENTIFIER, TokenType.CONTEXT, TokenType.FN) and ctx.stream.peek() and ctx.stream.peek().type in (TokenType.ASSIGN, TokenType.COLON):
                name = ctx.stream.current.value
                ctx.stream.advance()  # name
                # Accept either `=` or `:` as named argument separator
                ctx.stream.advance()  # consume ':' or '='

            value = parse_expression(ctx)
            arg_node = CallArgument(
                name=name,
                value=value,
                line=value.line if value else ctx.stream.pos,
                column=value.column if value else 0,
                file_path=ctx.source_file,
                parent=parent
            )
            if value and hasattr(value, 'parent'):
                value.parent = arg_node
            args.append(arg_node)

            if not ctx.stream.match(TokenType.COMMA):
                break
    ctx.stream.expect(TokenType.RPAREN)
    return args


def parse_array_literal(ctx: PositionTracker, parent: Optional[Any] = None) -> JsonArray:
    stream = ctx.stream
    tok = stream.expect(TokenType.LBRACKET)
    values = []
    
    if stream.current and stream.current.type != TokenType.RBRACKET:
        while True:
            expr = parse_expression(ctx)
            if expr:
                values.append(expr)
            if not stream.match(TokenType.COMMA):
                break
                
    stream.expect(TokenType.RBRACKET)
    
    # We use a simplified value for JsonArray in AST (list of values)
    # The actual JsonArray node might expect a raw list of Python values or AST nodes.
    # Looking at parse_primary, it seems it expects a list.
    return JsonArray(
        value=values,
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )


def parse_object_literal(ctx: PositionTracker, parent: Optional[Any] = None) -> JsonObject:
    stream = ctx.stream
    tok = stream.expect(TokenType.LBRACE)
    obj_dict = {}
    
    if stream.current and stream.current.type != TokenType.RBRACE:
        while True:
            # Key can be a string or identifier
            key_tok = stream.expect(TokenType.STRING, TokenType.IDENTIFIER)
            key = key_tok.value
            
            stream.expect(TokenType.COLON)
            value = parse_expression(ctx)
            if value:
                obj_dict[key] = value
                
            if not stream.match(TokenType.COMMA):
                break
                
    stream.expect(TokenType.RBRACE)
    
    return JsonObject(
        value=obj_dict,
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
