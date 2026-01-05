from typing import Any, List, Optional, Dict

from src.corplang.compiler.constants import PositionTracker, parse_block, SyntaxException
from src.corplang.compiler.lexer import TokenType
from src.corplang.compiler.nodes import (
    FunctionDeclaration, ClassDeclaration, MethodDeclaration, FieldDeclaration,
    ImportDeclaration, FromImportDeclaration, AgentDefinition, ModelDeclaration,
    MigrationDeclaration, AgentIntelligenceBlock, AgentContextBlock, AgentExecutionBlock,
    AgentAuthenticationBlock, AgentResourcesBlock, AgentObservabilityBlock,
    AgentTrain, AgentRun, AgentEmbed, AgentPredict, AgentShutdown,
    InterfaceDeclaration, ContractDeclaration, ModelField, RelationDeclaration,
    MigrationOperation, ModelConfigBlock, ModelArgument, AgentDefinition
)
from .expressions import parse_expression, parse_call_arguments

def parse_agent_statement(ctx: PositionTracker, parent: Optional[Any] = None) -> Any:
    stream = ctx.stream
    agent_tok = stream.expect(TokenType.AGENT)
    
    nxt = stream.current
    if not nxt:
        return None
        
    if nxt.type == TokenType.TRAIN:
        return parse_agent_train(ctx, parent)
    if nxt.type == TokenType.RUN:
        return parse_agent_run(ctx, parent)
    if nxt.type == TokenType.PREDICT:
        return parse_agent_predict(ctx, parent)
    if nxt.type == TokenType.STOP:
        return parse_agent_shutdown(ctx, parent)
    
    if nxt.type == TokenType.IDENTIFIER:
        name_tok = stream.expect(TokenType.IDENTIFIER)
        stream.expect(TokenType.LBRACE)
        
        node = AgentDefinition(
            name=name_tok.value,
            line=name_tok.line,
            column=name_tok.column,
            file_path=ctx.source_file,
            parent=parent
        )
        
        while stream.current and stream.current.type != TokenType.RBRACE:
            start_pos = stream.pos
            tok = stream.current
            if tok.type == TokenType.INTELLIGENCE:
                node.intelligence = parse_agent_intelligence(ctx, node)
            elif tok.type == TokenType.CONTEXT:
                node.context = parse_agent_context(ctx, node)
            elif tok.type == TokenType.EXECUTION:
                node.execution = parse_agent_execution(ctx, node)
            elif tok.type == TokenType.AUTHENTICATION:
                node.authentication = parse_agent_authentication(ctx, node)
            elif tok.type == TokenType.USING:
                # Assuming authentication or resources might use 'using'
                node.authentication = parse_agent_authentication(ctx, node)
            elif tok.type == TokenType.ANALYZE:
                node.observability = parse_agent_observability(ctx, node)
            elif tok.type == TokenType.DOCSTRING:
                node.docstring = tok.value
                stream.advance()
            else:
                stream.advance()
            
            if stream.pos == start_pos:
                stream.advance()
        
        stream.expect(TokenType.RBRACE)
        return node
    return None

def parse_agent_intelligence(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentIntelligenceBlock:
    stream = ctx.stream
    tok = stream.expect(TokenType.INTELLIGENCE)
    stream.expect(TokenType.LBRACE)
    
    node = AgentIntelligenceBlock(
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    while stream.current and stream.current.type != TokenType.RBRACE:
        inner = stream.current
        if inner.type == TokenType.PROVIDER:
            stream.advance()
            stream.match(TokenType.COLON)
            node.provider = stream.expect_identifier_like().value if stream.current.type in (TokenType.IDENTIFIER, TokenType.STRING) else stream.expect(TokenType.STRING).value
        elif inner.type == TokenType.CAPABILITY:
            stream.advance()
            stream.match(TokenType.COLON)
            node.capability = stream.expect_identifier_like().value if stream.current.type in (TokenType.IDENTIFIER, TokenType.STRING) else stream.expect(TokenType.STRING).value
        elif inner.type == TokenType.IDENTIFIER:
             key = stream.advance().value
             stream.match(TokenType.COLON)
             # Consume multiple values if no colon/newline/brace
             values = []
             while stream.current and stream.current.type not in (TokenType.RBRACE, TokenType.SEMICOLON, TokenType.COLON, TokenType.IDENTIFIER):
                 values.append(parse_expression(ctx, node))
             
             if len(values) == 1:
                 node.entries[key] = values[0]
             elif len(values) > 1:
                 node.entries[key] = values
        else:
            stream.advance()
    
    stream.expect(TokenType.RBRACE)
    return node

def parse_agent_context(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentContextBlock:
    stream = ctx.stream
    tok = stream.expect(TokenType.CONTEXT)
    stream.expect(TokenType.LBRACE)
    
    node = AgentContextBlock(
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    while stream.current and stream.current.type != TokenType.RBRACE:
        inner = stream.current
        if inner.type == TokenType.ALLOW:
            stream.advance()
            kind_tok = stream.match(TokenType.FUNCTION, TokenType.CLASS, TokenType.IDENTIFIER)
            kind = kind_tok.value if kind_tok else "intent"
            target_tok = stream.match(TokenType.IDENTIFIER, TokenType.STRING)
            target = target_tok.value if target_tok else "unknown"
            if kind in ("intent", "function", "mf"):
                node.allow_functions.append(target)
            elif kind == "class":
                node.allow_classes.append(target)
        elif inner.type == TokenType.DENY:
            stream.advance()
            target_tok = stream.match(TokenType.IDENTIFIER, TokenType.STRING)
            target = target_tok.value if target_tok else "unknown"
            node.deny.append(target)
        else:
            stream.advance()
            
    stream.expect(TokenType.RBRACE)
    return node

def parse_agent_execution(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentExecutionBlock:
    stream = ctx.stream
    tok = stream.expect(TokenType.EXECUTION)
    stream.expect(TokenType.LBRACE)
    
    node = AgentExecutionBlock(
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    while stream.current and stream.current.type != TokenType.RBRACE:
        inner = stream.current
        if inner.type == TokenType.ASYNC:
            stream.advance()
            stream.match(TokenType.COLON)
            node.async_exec = (stream.current.value == "true")
            stream.advance()
        elif inner.type == TokenType.IDENTIFIER:
            key = stream.advance().value
            stream.match(TokenType.COLON)
            node.entries[key] = parse_expression(ctx, node)
        else:
            stream.advance()
        
    stream.expect(TokenType.RBRACE)
    return node

def parse_agent_authentication(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentAuthenticationBlock:
    stream = ctx.stream
    tok = stream.match(TokenType.AUTHENTICATION, TokenType.USING)
    if not tok: return None
    
    stream.expect(TokenType.LBRACE)
    
    node = AgentAuthenticationBlock(
        line=tok.line, 
        column=tok.column, 
        file_path=ctx.source_file, 
        parent=parent
    )
    
    while stream.current and stream.current.type != TokenType.RBRACE:
        start_pos = stream.pos
        inner = stream.current
        if inner.type == TokenType.IDENTIFIER:
            key = stream.advance().value
            stream.match(TokenType.COLON)
            if stream.current and stream.current.type == TokenType.LBRACE:
                # Nested block in authentication
                stream.advance() # consume {
                nested_entries = {}
                while stream.current and stream.current.type != TokenType.RBRACE:
                    if stream.current.type == TokenType.IDENTIFIER:
                        n_key = stream.advance().value
                        stream.match(TokenType.COLON)
                        nested_entries[n_key] = parse_expression(ctx, node)
                    else:
                        stream.advance()
                stream.match(TokenType.RBRACE)
                node.entries[key] = nested_entries
            else:
                node.entries[key] = parse_expression(ctx, node)
        else:
            stream.advance()
            
        if stream.pos == start_pos:
            stream.advance()
            
    stream.match(TokenType.RBRACE)
    return node

def parse_agent_observability(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentObservabilityBlock:
    stream = ctx.stream
    tok = stream.expect(TokenType.ANALYZE)
    stream.expect(TokenType.LBRACE)
    node = AgentObservabilityBlock(line=tok.line, column=tok.column, file_path=ctx.source_file, parent=parent)
    while stream.current and stream.current.type != TokenType.RBRACE:
        stream.advance()
    stream.expect(TokenType.RBRACE)
    return node

def parse_agent_train(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentTrain:
    stream = ctx.stream
    train_tok = stream.expect(TokenType.TRAIN)
    name_tok = stream.expect(TokenType.IDENTIFIER)
    params = {}
    if stream.match(TokenType.WITH):
        if stream.match(TokenType.LBRACE):
            while stream.current and stream.current.type != TokenType.RBRACE:
                key = stream.expect(TokenType.IDENTIFIER).value
                stream.match(TokenType.COLON)
                params[key] = parse_expression(ctx)
                if not stream.match(TokenType.COMMA): break
            stream.expect(TokenType.RBRACE)
        else:
            # Single value or identifier
            params["source"] = parse_expression(ctx)

    stream.match(TokenType.SEMICOLON)
    return AgentTrain(
        agent_name=name_tok.value, 
        params=params,
        line=train_tok.line, 
        column=train_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )

def parse_agent_run(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentRun:
    stream = ctx.stream
    run_tok = stream.expect(TokenType.RUN)
    name_tok = stream.expect(TokenType.IDENTIFIER)
    args = {}
    if stream.match(TokenType.LPAREN):
        while stream.current and stream.current.type != TokenType.RPAREN:
            key = stream.expect(TokenType.IDENTIFIER).value
            stream.expect(TokenType.ASSIGN)
            args[key] = parse_expression(ctx)
            if not stream.match(TokenType.COMMA): break
        stream.expect(TokenType.RPAREN)

    return AgentRun(
        agent_name=name_tok.value, 
        args=args,
        line=run_tok.line, 
        column=run_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )

def parse_agent_predict(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentPredict:
    stream = ctx.stream
    predict_tok = stream.expect(TokenType.PREDICT)
    name_tok = stream.expect(TokenType.IDENTIFIER)
    stream.expect(TokenType.LPAREN)
    input_data = parse_expression(ctx)
    stream.expect(TokenType.RPAREN)
    return AgentPredict(
        agent_name=name_tok.value, 
        input_data=input_data,
        line=predict_tok.line, 
        column=predict_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )

def parse_agent_shutdown(ctx: PositionTracker, parent: Optional[Any] = None) -> AgentShutdown:
    stream = ctx.stream
    stop_tok = stream.expect(TokenType.STOP)
    name_tok = stream.expect(TokenType.IDENTIFIER)
    stream.match(TokenType.SEMICOLON)
    return AgentShutdown(
        agent_name=name_tok.value,
        line=stop_tok.line,
        column=stop_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )

def parse_function_declaration(ctx: PositionTracker, parent: Optional[Any] = None, is_async: bool = False) -> FunctionDeclaration:
    stream = ctx.stream
    # Support both 'intent' and 'fn' as keywords for functions
    fn_tok = stream.match(TokenType.FUNCTION, TokenType.FN)
    if not fn_tok:
        raise SyntaxException(stream.current.line, stream.current.column, stream.pos, "intent or fn", stream.current.type.name)
    
    name_tok = stream.expect_identifier_like()
    
    # Support generic parameters: intent contains<T>(...)
    generic_params = []
    if stream.match(TokenType.LESS_THAN):
        while True:
            generic_params.append(stream.expect_identifier_like().value)
            if not stream.match(TokenType.COMMA): break
        stream.expect(TokenType.GREATER_THAN)

    stream.expect(TokenType.LPAREN)
    params: List[str] = []
    param_types: Dict[str, Optional[str]] = {}
    param_defaults: Dict[str, Any] = {}
    
    if stream.current.type != TokenType.RPAREN:
        while True:
            # Use expect_identifier_like for parameter names
            p_name_tok = stream.expect_identifier_like()
            p_name = p_name_tok.value
            params.append(p_name)
            p_type = None
            if stream.match(TokenType.COLON):
                p_type = ctx.format_type(ctx.parse_type())
            param_types[p_name] = p_type
            
            if stream.match(TokenType.ASSIGN):
                param_defaults[p_name] = parse_expression(ctx)
            
            if not stream.match(TokenType.COMMA):
                break
    stream.expect(TokenType.RPAREN)
    
    return_type = None
    if stream.match(TokenType.COLON) or stream.match(TokenType.MINUS):
        if stream.current and stream.current.type == TokenType.GREATER_THAN:
            stream.advance()
        return_type = ctx.format_type(ctx.parse_type())
        
    node = FunctionDeclaration(
        name=name_tok.value,
        params=params,
        param_types=param_types,
        param_defaults=param_defaults,
        return_type=return_type,
        generic_params=generic_params if generic_params else None,
        body=[],
        is_async=is_async,
        line=fn_tok.line,
        column=fn_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    node.body = parse_block(ctx, node)
    return node

def parse_import_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> ImportDeclaration:
    stream = ctx.stream
    tok = stream.expect(TokenType.IMPORT)
    
    # Support dotted module paths
    parts = [stream.expect_identifier_like().value]
    while stream.match(TokenType.DOT):
        parts.append(stream.expect_identifier_like().value)
    module_path = ".".join(parts)
    
    stream.match(TokenType.SEMICOLON)
    return ImportDeclaration(
        module=module_path,
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )

def parse_from_import_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> FromImportDeclaration:
    stream = ctx.stream
    tok = stream.expect(TokenType.FROM)
    
    # Support dotted module paths
    parts = [stream.expect_identifier_like().value]
    while stream.match(TokenType.DOT):
        parts.append(stream.expect_identifier_like().value)
    module_path = ".".join(parts)
    
    stream.expect(TokenType.IMPORT)
    
    items = []
    while True:
        items.append(stream.expect_identifier_like().value)
        if not stream.match(TokenType.COMMA):
            break
            
    stream.match(TokenType.SEMICOLON)
    return FromImportDeclaration(
        module=module_path,
        items=items,
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )

def parse_model_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> ModelDeclaration:
    stream = ctx.stream
    tok = stream.expect(TokenType.MODEL)
    name_tok = stream.expect_identifier_like()
    stream.expect(TokenType.LBRACE)
    
    node = ModelDeclaration(
        name=name_tok.value,
        fields=[],
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    while stream.current and stream.current.type != TokenType.RBRACE:
        if stream.current.type in (TokenType.IDENTIFIER, TokenType.STRING) or stream.current.type in stream.tokens: # actually any allowed identifier
             # Use a more liberal check for field names
             f_name_tok = stream.expect_identifier_like()
             f_name = f_name_tok.value
             stream.expect(TokenType.COLON)
             f_type = ctx.format_type(ctx.parse_type())
             field = ModelField(
                 name=f_name,
                 type_annotation=f_type,
                 line=stream.current.line,
                 column=stream.current.column,
                 file_path=ctx.source_file,
                 parent=node
             )
             node.fields.append(field)
        else:
            stream.advance()
        
    stream.expect(TokenType.RBRACE)
    return node

def parse_migration_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> MigrationDeclaration:
    stream = ctx.stream
    tok = stream.expect(TokenType.MIGRATION)
    name_tok = stream.expect(TokenType.IDENTIFIER)
    stream.expect(TokenType.LBRACE)
    
    node = MigrationDeclaration(
        name=name_tok.value,
        up=[],
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    while stream.current and stream.current.type != TokenType.RBRACE:
        if stream.current.type == TokenType.IDENTIFIER:
            op_name = stream.advance().value
            stream.expect(TokenType.LPAREN)
            # Parse simple args as dict for now
            args = {}
            while stream.current and stream.current.type != TokenType.RPAREN:
                 k = stream.expect(TokenType.IDENTIFIER).value
                 stream.expect(TokenType.ASSIGN)
                 v = parse_expression(ctx).value # Simple literals
                 args[k] = v
                 if not stream.match(TokenType.COMMA): break
            stream.expect(TokenType.RPAREN)
            node.up.append(MigrationOperation(op=op_name, args=args, line=tok.line, column=tok.column, file_path=ctx.source_file, parent=node))
        else:
            stream.advance()
        
    stream.expect(TokenType.RBRACE)
    return node

def parse_class_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> ClassDeclaration:
    stream = ctx.stream
    # Handle both 'class' and 'driver'
    class_tok = stream.match(TokenType.CLASS, TokenType.DRIVER)
    if not class_tok:
        raise SyntaxException(stream.current.line, stream.current.column, stream.pos, "class or driver", stream.current.type.name)
    
    name_tok = stream.expect_identifier_like()
    
    generic_params = []
    if stream.match(TokenType.LESS_THAN):
        while True:
            generic_params.append(stream.expect_identifier_like().value)
            if not stream.match(TokenType.COMMA): break
        stream.expect(TokenType.GREATER_THAN)

    extends = None
    if stream.match(TokenType.EXTENDS):
        # Support potentially generic extends
        ext_type = ctx.parse_type()
        extends = ctx.format_type(ext_type)

    implements = []
    if stream.match(TokenType.IMPLEMENTS):
        while True:
            impl_type = ctx.parse_type()
            implements.append(ctx.format_type(impl_type))
            if not stream.match(TokenType.COMMA):
                break
        
    node = ClassDeclaration(
        name=name_tok.value,
        extends=extends,
        implements=implements if implements else None,
        generic_params=generic_params if generic_params else None,
        type_parameters=generic_params if generic_params else None,
        body=[],
        is_driver=(class_tok.type == TokenType.DRIVER),
        line=class_tok.line,
        column=class_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
        
    stream.expect(TokenType.LBRACE)
    while stream.current and stream.current.type != TokenType.RBRACE:
        tok = stream.current
        if tok.type == TokenType.DOCSTRING:
            node.docstring = tok.value
            stream.advance()
            continue

        is_private = stream.match(TokenType.PRIVATE) is not None
        is_protected = stream.match(TokenType.PROTECTED) is not None
        is_static = stream.match(TokenType.STATIC) is not None
        is_abstract = stream.match(TokenType.ABSTRACT) is not None
        is_async = stream.match(TokenType.ASYNC) is not None
        
        # In case modifiers are in different order
        while True:
            if not is_private and stream.match(TokenType.PRIVATE): is_private = True
            elif not is_protected and stream.match(TokenType.PROTECTED): is_protected = True
            elif not is_static and stream.match(TokenType.STATIC): is_static = True
            elif not is_abstract and stream.match(TokenType.ABSTRACT): is_abstract = True
            elif not is_async and stream.match(TokenType.ASYNC): is_async = True
            else: break
        
        if stream.current.type in (TokenType.FUNCTION, TokenType.FN):
             node.body.append(parse_method_declaration(ctx, node, is_private=is_private, is_static=is_static, is_abstract=is_abstract, is_async=is_async))
        elif stream.current.type in (TokenType.VAR, TokenType.IDENTIFIER):
             node.body.append(parse_field_declaration(ctx, node, is_private=is_private, is_static=is_static))
        else:
             stream.advance()
             
    stream.expect(TokenType.RBRACE)
    
    for member in node.body:
        if hasattr(member, 'parent'):
            member.parent = node
            
    return node

def parse_method_declaration(ctx: PositionTracker, parent: Optional[Any] = None, is_private: bool = False, is_static: bool = False, is_abstract: bool = False, is_async: bool = False, has_body: bool = True) -> MethodDeclaration:
    stream = ctx.stream
    fn_tok = stream.match(TokenType.FUNCTION, TokenType.FN)
    if not fn_tok:
        raise SyntaxException(stream.current.line, stream.current.column, stream.pos, "intent or fn", stream.current.type.name)
    
    name_tok = stream.expect_identifier_like()
    
    # Support generic parameters: intent contains<T>(...)
    generic_params = []
    if stream.match(TokenType.LESS_THAN):
        while True:
            generic_params.append(stream.expect_identifier_like().value)
            if not stream.match(TokenType.COMMA): break
        stream.expect(TokenType.GREATER_THAN)

    stream.expect(TokenType.LPAREN)
    params: List[str] = []
    param_types: Dict[str, Optional[str]] = {}
    param_defaults: Dict[str, Any] = {}
    
    if stream.current.type != TokenType.RPAREN:
        while True:
            # Use expect_identifier_like for parameter names
            p_name_tok = stream.expect_identifier_like()
            p_name = p_name_tok.value
            params.append(p_name)
            p_type = None
            if stream.match(TokenType.COLON):
                p_type = ctx.format_type(ctx.parse_type())
            param_types[p_name] = p_type
            
            if stream.match(TokenType.ASSIGN):
                param_defaults[p_name] = parse_expression(ctx)
                
            if not stream.match(TokenType.COMMA):
                break
    stream.expect(TokenType.RPAREN)
    
    return_type = None
    if stream.match(TokenType.COLON) or stream.match(TokenType.MINUS):
        if stream.current and stream.current.type == TokenType.GREATER_THAN:
            stream.advance()
        return_type = ctx.format_type(ctx.parse_type())
        
    docstring = None
    if stream.current and stream.current.type == TokenType.DOCSTRING:
        docstring = stream.current.value
        stream.advance()
        
    node = MethodDeclaration(
        name=name_tok.value,
        params=params,
        param_types=param_types,
        param_defaults=param_defaults,
        return_type=return_type,
        generic_params=generic_params if generic_params else None,
        docstring=docstring,
        body=[],
        is_private=is_private,
        is_static=is_static,
        is_async=is_async,
        line=fn_tok.line,
        column=fn_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    if has_body and stream.current and stream.current.type == TokenType.LBRACE:
        node.body = parse_block(ctx, node)
    elif has_body and not is_abstract:
         # Some methods might not have a body but are not abstract (e.g. native)
         # But for now, if it's not abstract and has_body is true, we expect a block.
         # Actually, let's just not force it if it's not a LBRACE.
         pass
        
    return node

def parse_field_declaration(ctx: PositionTracker, parent: Optional[Any] = None, is_private: bool = False, is_static: bool = False) -> FieldDeclaration:
    stream = ctx.stream
    has_var = stream.match(TokenType.VAR)
    name_tok = stream.expect_identifier_like()
    
    type_annotation = None
    if stream.match(TokenType.COLON):
        ta = ctx.parse_type()
        type_annotation = ctx.format_type(ta)
        
    value = None
    if stream.match(TokenType.ASSIGN):
        value = parse_expression(ctx)
        
    stream.match(TokenType.SEMICOLON)
    
    node = FieldDeclaration(
        name=name_tok.value,
        value=value,
        type_annotation=type_annotation,
        is_private=is_private,
        is_static=is_static,
        line=name_tok.line,
        column=name_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    if value and hasattr(value, 'parent'):
        value.parent = node
    return node

def parse_interface_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> InterfaceDeclaration:
    stream = ctx.stream
    tok = stream.expect(TokenType.INTERFACE)
    name_tok = stream.expect(TokenType.IDENTIFIER)
    
    generic_params = []
    if stream.match(TokenType.LESS_THAN):
        while True:
            generic_params.append(stream.expect(TokenType.IDENTIFIER).value)
            if not stream.match(TokenType.COMMA): break
        stream.expect(TokenType.GREATER_THAN)

    extends = []
    if stream.match(TokenType.EXTENDS):
        while True:
            extends.append(stream.expect(TokenType.IDENTIFIER).value)
            if not stream.match(TokenType.COMMA):
                break
                
    node = InterfaceDeclaration(
        name=name_tok.value,
        methods=[],
        extends=extends if extends else None,
        generic_params=generic_params if generic_params else None,
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    stream.expect(TokenType.LBRACE)
    while stream.current and stream.current.type != TokenType.RBRACE:
        if stream.current.type in (TokenType.FUNCTION, TokenType.FN):
            meth = parse_method_declaration(ctx, node, has_body=False)
            node.methods.append(meth)
        else:
            stream.advance()
    stream.expect(TokenType.RBRACE)
    return node

def parse_contract_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> ContractDeclaration:
    stream = ctx.stream
    tok = stream.expect(TokenType.CONTRACT)
    name_tok = stream.expect(TokenType.IDENTIFIER)
    
    generic_params = []
    if stream.match(TokenType.LESS_THAN):
        while True:
            generic_params.append(stream.expect(TokenType.IDENTIFIER).value)
            if not stream.match(TokenType.COMMA): break
        stream.expect(TokenType.GREATER_THAN)

    extends = []
    if stream.match(TokenType.EXTENDS):
        while True:
            extends.append(stream.expect(TokenType.IDENTIFIER).value)
            if not stream.match(TokenType.COMMA):
                break
                
    node = ContractDeclaration(
        name=name_tok.value,
        methods=[],
        extends=extends if extends else None,
        generic_params=generic_params if generic_params else None,
        line=tok.line,
        column=tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    stream.expect(TokenType.LBRACE)
    while stream.current and stream.current.type != TokenType.RBRACE:
        if stream.current.type in (TokenType.FUNCTION, TokenType.FN):
            node.methods.append(parse_method_declaration(ctx, node, has_body=False))
        else:
            stream.advance()
    stream.expect(TokenType.RBRACE)
    return node
