"""AST node for enum declaration."""
from typing import Any, List, Optional, Dict


class EnumDeclaration:
    """AST node for enum declaration at module level.
    
    Example:
        enum UserRole {
            ADMIN,
            CUSTOMER,
            EMPLOYED,
            STAFF
        }
    """
    def __init__(
        self,
        name: str,
        members: List[str],  # List of member names
        member_values: Optional[Dict[str, str]] = None,  # Optional explicit values
        line: int = 0,
        column: int = 0,
        file_path: str = "",
        parent: Optional[Any] = None
    ):
        self.name = name
        self.members = members
        self.member_values = member_values or {}  # Dict of name -> value
        self.line = line
        self.column = column
        self.file_path = file_path
        self.parent = parent
    
    def __repr__(self) -> str:
        return f"EnumDeclaration(name={self.name}, members={self.members})"
