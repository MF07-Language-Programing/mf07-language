"""Base migration driver interface."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MigrationDriver(ABC):
    """Base class for database-specific migration handlers."""
    
    @staticmethod
    @abstractmethod
    def get_field_type(field_def: Dict[str, Any]) -> str:
        """Convert field definition to SQL type for target database."""
        pass
    
    @staticmethod
    @abstractmethod
    def apply_operations(conn: Any, operations: List[Dict[str, Any]], graph: Dict[str, Any]) -> None:
        """Apply migration operations to database connection."""
        pass
    
    @staticmethod
    def _sql_value(val: Any) -> str:
        """Format Python value as SQL literal."""
        if val is None:
            return "NULL"
        if isinstance(val, bool):
            return "TRUE" if val else "FALSE"
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, str):
            return f"'{val.replace(chr(39), chr(39)+chr(39))}'"
        return str(val)
