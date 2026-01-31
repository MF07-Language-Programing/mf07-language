"""Parser function for enum declarations."""
from typing import Any, List, Optional, Dict
from src.corplang.compiler.constants import PositionTracker, SyntaxException
from src.corplang.compiler.lexer import TokenType
from src.corplang.compiler.nodes import EnumDeclaration


def parse_enum_declaration(ctx: PositionTracker, parent: Optional[Any] = None) -> EnumDeclaration:
    """Parse enum declaration.
    
    Syntax:
        enum UserRole {
            ADMIN,
            CUSTOMER,
            EMPLOYED,
            STAFF
        }
    
    Optional explicit values:
        enum Status {
            PENDING = "pending",
            ACTIVE = "active",
            CLOSED = "closed"
        }
    """
    stream = ctx.stream
    enum_tok = stream.expect(TokenType.ENUM)
    name_tok = stream.expect_identifier_like()
    enum_name = name_tok.value
    
    stream.expect(TokenType.LBRACE)
    
    members: List[str] = []
    member_values: Dict[str, str] = {}
    
    while stream.current and stream.current.type != TokenType.RBRACE:
        # Parse member name
        if stream.current.type != TokenType.IDENTIFIER:
            stream.advance()
            continue
        
        member_tok = stream.expect_identifier_like()
        member_name = member_tok.value
        members.append(member_name)
        
        # Check for explicit value: ADMIN = "admin"
        if stream.match(TokenType.ASSIGN):
            if stream.current and stream.current.type == TokenType.STRING:
                value_tok = stream.current
                value = value_tok.value.strip('"\'')
                member_values[member_name] = value
                stream.advance()
            else:
                # Try to parse as literal
                value = stream.current.value if stream.current else member_name.lower()
                member_values[member_name] = value
                stream.advance()
        else:
            # Default: member name in lowercase becomes the value
            member_values[member_name] = member_name.lower()
        
        # Optional comma
        stream.match(TokenType.COMMA)
    
    stream.expect(TokenType.RBRACE)
    
    node = EnumDeclaration(
        name=enum_name,
        members=members,
        member_values=member_values,
        line=enum_tok.line,
        column=enum_tok.column,
        file_path=ctx.source_file,
        parent=parent
    )
    
    return node
