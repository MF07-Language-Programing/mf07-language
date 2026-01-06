from typing import Any, List, Optional
from src.corplang.compiler.lexer import TokenType
from src.corplang.compiler.nodes import (
    VarDeclaration, IfStatement, WhileStatement, ForStatement, ForInStatement,
    ReturnStatement, BreakStatement, ContinueStatement, TryStatement, CatchClause,
    ThrowStatement, WithStatement, WithItem, LoopStatement, ServeStatement, StopStatement,
    ForOfStatement, DeleteStatement
)
from src.corplang.compiler.constants import PositionTracker, parse_block, separated
from src.corplang.compiler.constants.core import SyntaxException
from .expressions import parse_expression

def parse_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    stream = ctx.stream
    tok = stream.current
    if not tok:
        return None

    if tok.type == TokenType.VAR:
        return parse_var_declaration(ctx, parent)
    elif tok.type == TokenType.IF:
        return parse_if_statement(ctx, parent)
    elif tok.type == TokenType.WHILE:
        return parse_while_statement(ctx, parent)
    elif tok.type == TokenType.FOR:
        return parse_for_statement(ctx, parent)
    elif tok.type == TokenType.TRY:
        return parse_try_statement(ctx, parent)
    elif tok.type == TokenType.THROW:
        return parse_throw_statement(ctx, parent)
    elif tok.type == TokenType.WITH:
        return parse_with_statement(ctx, parent)
    elif tok.type == TokenType.SERVE:
        return parse_serve_statement(ctx, parent)
    elif tok.type == TokenType.STOP:
        return parse_stop_statement(ctx, parent)
    elif tok.type == TokenType.DELETE:
        return parse_delete_statement(ctx, parent)
    elif tok.type == TokenType.LOOP:
        return parse_loop_statement(ctx, parent)
    elif tok.type == TokenType.RETURN:
        return parse_return_statement(ctx, parent)
    elif tok.type == TokenType.BREAK:
        stream.advance()
        stream.match(TokenType.SEMICOLON)
        return BreakStatement(line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
    elif tok.type == TokenType.CONTINUE:
        stream.advance()
        stream.match(TokenType.SEMICOLON)
        return ContinueStatement(line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
    
    # Default to expression statement
    expr = parse_expression(ctx, parent)
    stream.match(TokenType.SEMICOLON)
    return expr

def parse_loop_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> LoopStatement:
    stream = ctx.stream
    tok = stream.expect(TokenType.LOOP)
    adapter = None
    agent_names = None
    
    # Check for 'loop stdin using Agent'
    if stream.current and stream.current.type == TokenType.IDENTIFIER and stream.current.value == "stdin":
        adapter = stream.advance().value
        if stream.match(TokenType.USING):
            agent_names = [stream.expect(TokenType.IDENTIFIER).value]
        
        return LoopStatement(
            adapter=adapter, 
            agent_names=agent_names, 
            body=[], 
            line=tok.line, 
            column=tok.column, 
            file_path=ctx.source_file, 
            parent=parent
        )
            
    node = LoopStatement(body=[], line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
    # Allow single-statement bodies without braces
    if stream.current and stream.current.type == TokenType.LBRACE:
        node.body = parse_block(ctx, node)
    else:
        # Skip blank lines before single-statement bodies
        while stream.current and stream.current.type == TokenType.NEWLINE:
            stream.advance()
        stmt = ctx.parse_statement(node)
        node.body = [stmt] if stmt else []
    return node

def parse_serve_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> ServeStatement:
    stream = ctx.stream
    tok = stream.expect(TokenType.SERVE)
    # serve http port 8361 name secureagentserver using MySecureAgent
    adapter = stream.expect_identifier_like().value
    
    params = {"adapter": adapter}
    while stream.current and stream.current.type != TokenType.SEMICOLON:
        start_pos = stream.pos
        key_tok = stream.match(TokenType.IDENTIFIER, TokenType.USING)
        if not key_tok: 
            if stream.pos == start_pos:
                stream.advance()
            break
        
        key = key_tok.value
        if key == "using":
            params["agent_names"] = [stream.expect(TokenType.IDENTIFIER).value]
        elif key == "port":
            val_tok = stream.expect(TokenType.NUMBER)
            params["port"] = int(val_tok.value)
        elif key == "host":
            val_tok = stream.expect(TokenType.STRING, TokenType.IDENTIFIER)
            params["host"] = val_tok.value
        elif key == "name":
            val_tok = stream.expect(TokenType.STRING, TokenType.IDENTIFIER)
            params["name"] = val_tok.value
        else:
            val_tok = stream.match(TokenType.NUMBER, TokenType.STRING, TokenType.IDENTIFIER)
            if val_tok:
                params[key] = val_tok.value
            
    stream.match(TokenType.SEMICOLON)
    return ServeStatement(
        adapter=params.get("adapter", "http"),
        port=params.get("port"),
        host=params.get("host"),
        name=params.get("name", "unnamed"),
        agent_names=params.get("agent_names"),
        line=tok.line, 
        column=tok.column, 
        file_path=ctx.source_file, 
        parent=parent
    )

def parse_stop_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> StopStatement:
    stream = ctx.stream
    tok = stream.expect(TokenType.STOP)
    target = stream.expect(TokenType.IDENTIFIER).value
    stream.match(TokenType.SEMICOLON)
    return StopStatement(target=target, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)

def parse_delete_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> DeleteStatement:
    stream = ctx.stream
    tok = stream.expect(TokenType.DELETE)
    target = parse_expression(ctx, parent)
    stream.match(TokenType.SEMICOLON)
    node = DeleteStatement(target=target, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
    if hasattr(target, 'parent'):
        target.parent = node
    return node

def parse_for_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    stream = ctx.stream
    for_tok = stream.expect(TokenType.FOR)
    stream.expect(TokenType.LPAREN)
    
    # Check if it's a standard C-style for loop: for (init; cond; step)
    # We look ahead to see if there's a semicolon after some expression/declaration
    
    # Case: for (var i = 0; ...)
    if stream.current.type == TokenType.VAR:
        # It could be ForIn or ForOf if it follows: var x in ... or var x of ...
        # Let's peek ahead
        if stream.peek(2) and stream.peek(2).type == TokenType.IN:
            return parse_for_in_statement(ctx, for_tok, parent)
        if stream.peek(2) and stream.peek(2).type == TokenType.OF:
            return parse_for_of_statement(ctx, for_tok, parent)
            
        # Standard for loop
        return parse_standard_for_statement(ctx, for_tok, parent)

    # Case: for (i = 0; ...) or for (i in ...)
    if stream.current.type == TokenType.IDENTIFIER:
        if stream.peek() and stream.peek().type == TokenType.IN:
            return parse_for_in_statement(ctx, for_tok, parent)
        if stream.peek() and stream.peek().type == TokenType.OF:
            return parse_for_of_statement(ctx, for_tok, parent)
            
        return parse_standard_for_statement(ctx, for_tok, parent)
        
    # Default to standard for loop
    return parse_standard_for_statement(ctx, for_tok, parent)

def parse_standard_for_statement(ctx: PositionTracker, for_tok: Any, parent: Optional[Any] = None) -> ForStatement:
    stream = ctx.stream
    # for ( [init] ; [cond] ; [step] )
    
    init = None
    if stream.current.type != TokenType.SEMICOLON:
        if stream.current.type == TokenType.VAR:
            init = parse_var_declaration(ctx, parent)
        else:
            init = parse_expression(ctx, parent)
            stream.match(TokenType.SEMICOLON)
    else:
        stream.advance() # ;
        
    condition = None
    if stream.current.type != TokenType.SEMICOLON:
        condition = parse_expression(ctx)
    stream.expect(TokenType.SEMICOLON)
    
    step = None
    if stream.current.type != TokenType.RPAREN:
        step = parse_expression(ctx)
    stream.expect(TokenType.RPAREN)
    
    node = ForStatement(
        init=init,
        condition=condition,
        update=step,
        body=[],
        line=for_tok.line,
        column=for_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if init and hasattr(init, 'parent'): init.parent = node
    if condition and hasattr(condition, 'parent'): condition.parent = node
    if step and hasattr(step, 'parent'): step.parent = node
    
    # Allow single-statement bodies without braces
    if stream.current and stream.current.type == TokenType.LBRACE:
        node.body = parse_block(ctx, node)
    else:
        # Skip blank lines before single-statement bodies
        while stream.current and stream.current.type == TokenType.NEWLINE:
            stream.advance()
        stmt = ctx.parse_statement(node)
        node.body = [stmt] if stmt else []
    return node

def parse_for_of_statement(ctx: PositionTracker, for_tok: Any, parent: Optional[Any] = None) -> ForOfStatement:
    stream = ctx.stream
    stream.match(TokenType.VAR)
    var_tok = stream.expect(TokenType.IDENTIFIER)
    stream.expect(TokenType.OF)
    iterable = parse_expression(ctx)
    stream.expect(TokenType.RPAREN)
    
    node = ForOfStatement(
        variable=var_tok.value,
        iterable=iterable,
        body=[],
        line=for_tok.line,
        column=for_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if hasattr(iterable, 'parent'):
        iterable.parent = node
        
    node.body = parse_block(ctx, node)
    return node

def parse_for_in_statement(ctx: PositionTracker, for_tok: Any, parent: Optional[Any] = None) -> ForInStatement:
    stream = ctx.stream
    # for ( [var] x in iterable )
    stream.match(TokenType.VAR)
    var_tok = stream.expect(TokenType.IDENTIFIER)
    stream.expect(TokenType.IN)
    iterable = parse_expression(ctx)
    stream.expect(TokenType.RPAREN)
    
    node = ForInStatement(
        variable=var_tok.value,
        iterable=iterable,
        body=[],
        line=for_tok.line,
        column=for_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if hasattr(iterable, 'parent'):
        iterable.parent = node
        
    node.body = parse_block(ctx, node)
    return node

def parse_try_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> TryStatement:
    stream = ctx.stream
    try_tok = stream.expect(TokenType.TRY)
    try_block = parse_block(ctx)
    
    catch_clauses = []
    while stream.current and stream.current.type == TokenType.CATCH:
        catch_tok = stream.advance() # catch
        
        # Support both catch(e: Type) and catch e: Type
        has_paren = stream.match(TokenType.LPAREN)
        
        exc_type = None
        exc_var = None
        
        if stream.current.type == TokenType.IDENTIFIER:
            exc_var = stream.expect(TokenType.IDENTIFIER).value
            if not stream.match(TokenType.COLON):
                raise SyntaxException(catch_tok.line, catch_tok.column, stream.pos, "typed catch", "untyped catch")
            exc_type = ctx.parse_type()
            try:
                if getattr(exc_type, "base", "").lower() == "any":
                    raise SyntaxException(catch_tok.line, catch_tok.column, stream.pos, "specific exception type", "any")
            except Exception:
                pass
        
        if has_paren:
            stream.expect(TokenType.RPAREN)
        
        c_node = CatchClause(
            exception_type=exc_type,
            exception_var=exc_var,
            body=[],
            line=catch_tok.line,
            column=catch_tok.column,
            file_path=ctx.source_file,
            parent=None # will be set
        )
        c_node.body = parse_block(ctx, c_node)
        catch_clauses.append(c_node)
        
    finally_block = None
    if stream.match(TokenType.FINALLY):
        finally_block = parse_block(ctx)
        
    node = TryStatement(
        try_block=try_block,
        catch_clauses=catch_clauses,
        finally_block=finally_block,
        line=try_tok.line,
        column=try_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    for stmt in node.try_block:
        if hasattr(stmt, 'parent'): stmt.parent = node
    for clause in node.catch_clauses:
        clause.parent = node
    if node.finally_block:
        for stmt in node.finally_block:
            if hasattr(stmt, 'parent'): stmt.parent = node
            
    return node

def parse_throw_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> ThrowStatement:
    stream = ctx.stream
    tok = stream.expect(TokenType.THROW)
    expr = parse_expression(ctx)
    stream.match(TokenType.SEMICOLON)
    
    node = ThrowStatement(
        expression=expr,
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if hasattr(expr, 'parent'):
        expr.parent = node
    return node

def parse_with_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> WithStatement:
    stream = ctx.stream
    with_tok = stream.expect(TokenType.WITH)
    stream.expect(TokenType.LPAREN)
    
    items = []
    while True:
        expr = parse_expression(ctx)
        target = None
        if stream.match(TokenType.AS):
            target = stream.expect(TokenType.IDENTIFIER).value
            
        item = WithItem(
            context_expr=expr,
            target=target,
            line=expr.line,
            column=expr.column,
            file_path=ctx.source_file,
            parent=None # will be set
        )
        items.append(item)
        if not stream.match(TokenType.COMMA):
            break
    stream.expect(TokenType.RPAREN)
    
    node = WithStatement(
        items=items,
        body=[],
        line=with_tok.line,
        column=with_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    for item in items:
        item.parent = node
        if hasattr(item.context_expr, 'parent'):
            item.context_expr.parent = item
            
    node.body = parse_block(ctx, node)
    return node

def parse_var_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> VarDeclaration:
    stream = ctx.stream
    var_tok = stream.expect(TokenType.VAR)
    name_tok = stream.expect_identifier_like()
    
    type_annotation = None
    if stream.match(TokenType.COLON):
        type_annotation = ctx.parse_type()
    
    stream.expect(TokenType.ASSIGN)
    value = parse_expression(ctx) # Will be updated later to set parent
    stream.match(TokenType.SEMICOLON)
    
    node = VarDeclaration(
        name=name_tok.value,
        value=value,
        type_annotation=ctx.format_type(type_annotation) if type_annotation else None,
        line=var_tok.line,
        column=var_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if hasattr(value, 'parent'):
        value.parent = node
    return node

def parse_if_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> IfStatement:
    stream = ctx.stream
    if_tok = stream.expect(TokenType.IF)
    
    if stream.match(TokenType.LPAREN):
        condition = parse_expression(ctx)
        stream.expect(TokenType.RPAREN)
    else:
        condition = parse_expression(ctx)
    
    node = IfStatement(
        condition=condition,
        then_stmt=[],
        else_stmt=None,
        line=if_tok.line,
        column=if_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if hasattr(condition, 'parent'):
        condition.parent = node
    
    node.then_stmt = parse_block(ctx, node) if stream.current.type == TokenType.LBRACE else [parse_statement(ctx, node)]
    for stmt in node.then_stmt:
        if hasattr(stmt, 'parent'):
            stmt.parent = node
            
    if stream.match(TokenType.ELSE):
        if stream.current.type == TokenType.LBRACE:
            node.else_stmt = parse_block(ctx, node)
        else:
            node.else_stmt = [parse_statement(ctx, node)]
            
        if node.else_stmt:
            for stmt in node.else_stmt:
                if hasattr(stmt, 'parent'):
                    stmt.parent = node
            
    return node

def parse_while_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> WhileStatement:
    stream = ctx.stream
    while_tok = stream.expect(TokenType.WHILE)
    
    if stream.match(TokenType.LPAREN):
        condition = parse_expression(ctx)
        stream.expect(TokenType.RPAREN)
    else:
        condition = parse_expression(ctx)
        
    node = WhileStatement(
        condition=condition,
        body=[],
        line=while_tok.line,
        column=while_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if hasattr(condition, 'parent'):
        condition.parent = node
        
    node.body = parse_block(ctx, node)
    for stmt in node.body:
        if hasattr(stmt, 'parent'):
            stmt.parent = node
            
    return node

def parse_return_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> ReturnStatement:
    stream = ctx.stream
    ret_tok = stream.expect(TokenType.RETURN)
    value = None
    if stream.current and stream.current.type not in (TokenType.SEMICOLON, TokenType.RBRACE):
        value = parse_expression(ctx)
        
    node = ReturnStatement(
        value=value, 
        line=ret_tok.line, 
        column=ret_tok.column, 
        file_path=ctx.source_file, 
        parent=parent
    )
    if value and hasattr(value, 'parent'):
        value.parent = node
        
    stream.match(TokenType.SEMICOLON)
    return node
