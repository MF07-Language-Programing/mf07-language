"""Enum support: declarations and runtime objects."""
from __future__ import annotations
from typing import Any, Dict, List, Optional


class EnumMember:
    """Single enum member with name and optional value."""
    __slots__ = ('name', 'value')
    
    def __init__(self, name: str, value: str = None):
        self.name = name
        self.value = value if value is not None else name.lower()
    
    def __repr__(self) -> str:
        return f"{self.name}={self.value!r}"


class EnumType:
    """Runtime enum type instance."""
    
    def __init__(self, name: str, members: List[EnumMember]):
        self.__name__ = name
        self.__members__ = {m.name: m for m in members}
        
        # Create member instances and set as attributes
        for member in members:
            inst = EnumValue(name, member.name, member.value)
            setattr(self, member.name, inst)
    
    def __repr__(self) -> str:
        members_str = ", ".join(f"{m.name}" for m in self.__members__.values())
        return f"<enum {self.__name__} {{{members_str}}}>"
    
    def __dir__(self) -> List[str]:
        return list(self.__members__.keys())


class EnumValue:
    """Individual enum value with name and value properties."""
    __slots__ = ('__enum_name__', '__name__', '__value__')
    
    def __init__(self, enum_name: str, name: str, value: str):
        object.__setattr__(self, '__enum_name__', enum_name)
        object.__setattr__(self, '__name__', name)
        object.__setattr__(self, '__value__', value)
    
    @property
    def name(self) -> str:
        """Get the enum member name."""
        return object.__getattribute__(self, '__name__')
    
    @property
    def value(self) -> str:
        """Get the enum member value."""
        return object.__getattribute__(self, '__value__')
    
    def __repr__(self) -> str:
        enum_name = object.__getattribute__(self, '__enum_name__')
        name = object.__getattribute__(self, '__name__')
        return f"{enum_name}.{name}"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, EnumValue):
            return (
                object.__getattribute__(self, '__enum_name__') == object.__getattribute__(other, '__enum_name__') and
                object.__getattribute__(self, '__name__') == object.__getattribute__(other, '__name__')
            )
        return False
    
    def __hash__(self) -> int:
        enum_name = object.__getattribute__(self, '__enum_name__')
        name = object.__getattribute__(self, '__name__')
        return hash((enum_name, name))
