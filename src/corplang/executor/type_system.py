"""Lightweight runtime type representation for the MF interpreter."""
from __future__ import annotations

from typing import Any, Iterable, Optional

from src.corplang.compiler.nodes import TypeAnnotation
from src.corplang.executor.objects import ClassObject, InstanceObject


_PRIMITIVE_ALIASES = {
    "string": {"string", "str"},
    "number": {"number", "int", "integer", "float", "double"},
    "boolean": {"boolean", "bool"},
    "list": {"list", "array"},
    "object": {"object", "map", "dict"},
    "function": {"function", "callable"},
    "null": {"null", "nil", "none"},
    "any": {"any"},
}


def _canonical(name: Optional[str]) -> str:
    if not name:
        return "any"
    lowered = str(name).strip().lower()
    for canon, aliases in _PRIMITIVE_ALIASES.items():
        if lowered in aliases:
            return canon
    return lowered


def _alias_set(name: Optional[str]) -> set[str]:
    canon = _canonical(name)
    aliases = set()
    for k, vals in _PRIMITIVE_ALIASES.items():
        if canon == k:
            aliases |= set(vals)
    if name:
        aliases.add(str(name))
    aliases.add(canon)
    return aliases


class TypeObject:
    def __init__(
        self,
        name: str,
        *,
        kind: str = "primitive",
        class_obj: Optional[ClassObject] = None,
        args: Optional[list["TypeObject"]] = None,
        union_types: Optional[list["TypeObject"]] = None,
        aliases: Optional[Iterable[str]] = None,
        is_any: bool = False,
    ) -> None:
        self.name = name
        self.kind = kind
        self.class_obj = class_obj
        self.args = args or []
        self.union_types = union_types or []
        self.is_any = is_any or _canonical(name) == "any"
        self.aliases = set(a.lower() for a in aliases or []) | _alias_set(name)
        self.canonical_name = _canonical(name)

    @property
    def display_name(self) -> str:
        if self.union_types:
            return "|".join(t.display_name for t in self.union_types)
        if self.args:
            inner = ", ".join(t.display_name for t in self.args)
            return f"{self.name}<{inner}>"
        return self.name

    def isAssignableTo(self, other: Any) -> bool:  # pragma: no cover - used from MP code
        return self.is_assignable_to(other)

    def is_assignable_to(self, other: Any) -> bool:
        other_obj = ensure_type_object(other)
        if other_obj is None:
            return False

        if other_obj.is_any or self.is_any:
            return True

        if other_obj.kind == "union":
            return any(self.is_assignable_to(t) for t in other_obj.union_types)

        if self.kind == "union":
            return any(t.is_assignable_to(other_obj) for t in self.union_types)

        if self.kind == "class" and other_obj.kind == "class":
            if self.class_obj is None or other_obj.class_obj is None:
                return self.canonical_name == other_obj.canonical_name
            cur = self.class_obj
            target = other_obj.class_obj
            while cur is not None:
                if getattr(cur, "name", None) == getattr(target, "name", None):
                    return True
                cur = getattr(cur, "parent", None)
            return False

        if self.kind == "primitive" and other_obj.kind == "primitive":
            return self.canonical_name == other_obj.canonical_name

        return self.canonical_name == other_obj.canonical_name

    def __repr__(self) -> str:
        return f"Type({self.display_name})"


def ensure_type_object(value: Any, interpreter: Any = None) -> Optional[TypeObject]:
    if isinstance(value, TypeObject):
        return value
    if isinstance(value, TypeAnnotation):
        return type_from_annotation(value, interpreter)
    if isinstance(value, str):
        return TypeObject(value, aliases=_alias_set(value))
    if value is None:
        return TypeObject("any", is_any=True)
    return None


def type_from_value(value: Any, interpreter: Any = None) -> TypeObject:
    if isinstance(value, TypeObject):
        return value

    if value is None:
        return TypeObject("null")

    if isinstance(value, bool):
        return TypeObject("boolean")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        alias = "int" if isinstance(value, int) else "float"
        return TypeObject(alias, aliases=_alias_set(alias))

    if isinstance(value, str):
        return TypeObject("string")

    if isinstance(value, (list, tuple)):
        return TypeObject("list")

    if isinstance(value, dict):
        return TypeObject("object")

    if isinstance(value, InstanceObject):
        cls = getattr(value, "class_obj", None)
        name = getattr(cls, "name", None) or getattr(value, "class_name", None) or type(value).__name__
        return TypeObject(name, kind="class", class_obj=cls)

    if isinstance(value, ClassObject):
        name = getattr(value, "name", None) or type(value).__name__
        return TypeObject(name, kind="class", class_obj=value)

    if callable(value):
        return TypeObject("function")

    return TypeObject(type(value).__name__, kind="native")


def type_from_annotation(annotation: Optional[TypeAnnotation], interpreter: Any = None) -> TypeObject:
    if annotation is None:
        return TypeObject("any", is_any=True)

    if getattr(annotation, "base", None) == "Union":
        types = [type_from_annotation(arg, interpreter) for arg in (annotation.args or [])]
        return TypeObject("Union", kind="union", union_types=types, aliases={"union"})

    base = getattr(annotation, "base", None) or "any"
    canon = _canonical(base)

    if canon in ("string", "number", "boolean", "list", "object", "function", "null", "any"):
        aliases = _alias_set(base)
        return TypeObject(base, kind="primitive", aliases=aliases, is_any=canon == "any")

    resolved = _resolve_class(base, interpreter)
    if resolved is not None:
        arg_types = [type_from_annotation(arg, interpreter) for arg in (annotation.args or [])]
        return TypeObject(base, kind="class", class_obj=resolved, args=arg_types)

    return TypeObject(base, aliases=_alias_set(base))


def _resolve_class(name: str, interpreter: Any = None) -> Optional[ClassObject]:
    if interpreter is None:
        return None
    ge = getattr(interpreter, "global_env", None)
    if ge is None:
        return None

    # Direct match
    try:
        if name in ge.variables:
            val = ge.variables[name]
            if isinstance(val, ClassObject):
                return val
    except Exception:
        pass

    # Walk nested namespaces (dicts)
    try:
        def _find(container):
            if isinstance(container, dict):
                if name in container and isinstance(container[name], ClassObject):
                    return container[name]
                for v in container.values():
                    found = _find(v)
                    if found is not None:
                        return found
            return None

        for _, val in (ge.variables or {}).items():
            found = _find(val)
            if found is not None:
                return found
    except Exception:
        pass

    # Attempt lazy import of exceptions module for core types
    try:
        if hasattr(interpreter, "_import_module") and name in ("Exception", "Error", "RuntimeError", "TypeError", "GenericContractError", "RuntimeException"):
            exports = interpreter._import_module("core.lang.exceptions", None)
            if isinstance(exports, dict) and name in exports and isinstance(exports[name], ClassObject):
                return exports[name]
    except Exception:
        pass

    return None
