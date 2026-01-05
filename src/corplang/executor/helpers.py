"""Minimal helpers used by the runtime and executor layers.

Provides:
- matches_type(value, expected_str)
- literal_type_name(value)
- frame(context, file, line, function, variables, node=None) -> contextmanager

This module is intentionally small and dependency-free to keep executor imports light.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.corplang.core.exceptions import RuntimeErrorType


def matches_type(value: Any, expected: str) -> bool:
    """Matches types for utility.

    Supports:
    - Primitives (string/int/float/bool/number/list/dict)
    - 'any' keyword (always matches)
    - Unions using '|' (e.g., int|float|string)
    - Class/instance checks by matching InstanceObject.class_name to expected
    """

    if not expected:
        return True

    # Handle unions like "int|float"
    if "|" in expected:
        for part in expected.split("|"):
            if matches_type(value, part.strip()):
                return True
        return False

    et = expected.strip().lower()

    if et == "any":
        return True

    if et in ("str", "string"):
        return isinstance(value, str)

    if et in ("int", "integer"):
        return isinstance(value, int) and not isinstance(value, bool)

    if et in ("float", "double"):
        return isinstance(value, float)

    if et in ("number",):
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if et in ("list", "array"):
        return isinstance(value, (list, tuple))

    if et in ("dict", "map", "object"):
        return isinstance(value, dict)

    if et in ("bool", "boolean"):
        return isinstance(value, bool)

    if et in ("function", "callable"):
        return callable(value)

    if et == "module":
        return isinstance(value, dict)

    # Class/instance name check: if value is an InstanceObject, compare names
    try:
        from src.corplang.executor.objects import InstanceObject, ClassObject

        if isinstance(value, InstanceObject):
            return getattr(value, "class_name", None) == expected
        if isinstance(value, ClassObject):
            return getattr(value, "name", None) == expected
    except Exception:
        # If import fails or checks fail, fallthrough to permissive
        pass

    # If we reach here, the expected type is not a known primitive or matched class
    # Be strict: unknown type annotations must match object/class instances
    return False


def literal_type_name(value: Any) -> str:
    """To literal name"""
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "number"

    if isinstance(value, str):
        return "string"

    if isinstance(value, (list, tuple)):
        return "list"

    if isinstance(value, dict):
        return "object"

    if callable(value):
        return "function"

    return type(value).__name__


# Helpers expected by executor/*
def get_node_attr(node: Any, *names: str, default: Any = None) -> Any:
    """Return the first attribute on node that exists among names, or default."""
    if node is None:
        return default

    for n in names:
        if hasattr(node, n):
            return getattr(node, n)
    return default


def resolve_node_value(node: Any, context: Any) -> Any:
    """Evaluate an AST node in the given context.

    If the node is not executable (no executor), return the node itself. All other
    exceptions raised by execution are propagated so user-level try/catch can
    handle runtime errors as intended.
    """
    if node is None:
        return None
    try:
        # context is an ExecutionContext
        return context.interpreter.execute(node, context)
    except LookupError:
        # No executor registered for this node: fall back to returning the node
        return node
    except Exception:
        # Propagate execution errors (e.g. runtime/typing/reference errors)
        raise


def type_check(value: Any, annotation: Any, strict_types: bool, error_class: Any, node: Optional[Any] = None) -> None:
    """Enforce simple runtime type checks when `strict_types` is True."""
    if annotation is None:
        return
    if not strict_types:
        return
    expected = str(annotation)
    if not matches_type(value, expected):
        raise error_class(
            f"Type mismatch: expected {expected}, got {literal_type_name(value)}",
            RuntimeErrorType.TYPE_ERROR,
            node=node,
        )

class _FrameCM:
    def __init__(self, ctx: Any, file: Optional[str], line: Optional[int], function: Optional[str], locals_map: Optional[Dict[str, Any]] = None, node: Optional[Any] = None):
        self._ctx = ctx
        self._file = file
        self._line = line
        self._function = function
        self._locals = dict(locals_map or {})
        self._node = node

    def __enter__(self):
        try:
            interp = getattr(self._ctx, "interpreter", None)
            if interp is not None:
                origin_file = getattr(self._node, "file", None) if self._node is not None else None
                origin_line = getattr(self._node, "line", None) if self._node is not None else None
                column = getattr(self._node, "column", None) if self._node is not None else None
                interp.push_frame(
                    self._file,
                    self._line,
                    self._function,
                    locals_map=self._locals,
                    column=column,
                    origin_file=origin_file,
                    origin_line=origin_line,
                )
        except Exception:
            pass
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            interp = getattr(self._ctx, "interpreter", None)
            if interp is not None:
                interp.pop_frame()
        except Exception:
            pass
        return False


def frame(ctx: Any, file: Optional[str], line: Optional[int], function: Optional[str], locals_map: Optional[Dict[str, Any]] = None, node: Optional[Any] = None):
    """Return a context-manager that pushes/pops interpreter frames for stack traces."""
    return _FrameCM(ctx, file, line, function, locals_map, node)
