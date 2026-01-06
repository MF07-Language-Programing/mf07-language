"""Expression-related node executors.

Includes literals, identifiers, binary/unary expressions, and JSON helpers.
"""

from __future__ import annotations

from typing import Any, List, Optional

from src.corplang.executor.node import NodeExecutor
from src.corplang.executor.context import ExecutionContext
from src.corplang.executor.helpers import (
    get_node_attr,
    resolve_node_value,
)
from src.corplang.executor.interpreter import ExecutorRegistry
from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType
from src.corplang.executor.objects import InstanceObject


class LiteralExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "Literal" or hasattr(node, "value")

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        return getattr(node, "value", None)


class NullLiteralExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "NullLiteral"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        return None


class IdentifierExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "Identifier" and hasattr(node, "name")

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        name = getattr(node, "name", None)
        try:
            return context.get_var(name)
        except Exception:
            raise CorpLangRuntimeError(
                f"Undefined variable: {name}", RuntimeErrorType.REFERENCE_ERROR, node=node
            )


class IndexAccessExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "IndexAccess"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        obj = resolve_node_value(get_node_attr(node, "obj", "object"), context)
        index_node = get_node_attr(node, "index", "key", "property")
        idx = resolve_node_value(index_node, context)

        if isinstance(obj, (list, tuple)):
            if not isinstance(idx, int):
                raise CorpLangRuntimeError(
                    f"List index must be integer, got {type(idx).__name__}",
                    RuntimeErrorType.TYPE_ERROR,
                    node=node,
                )
            if idx < 0 or idx >= len(obj):
                raise CorpLangRuntimeError(
                    f"Index {idx} out of range",
                    RuntimeErrorType.TYPE_ERROR,
                    node=node,
                )
            return obj[idx]

        if isinstance(obj, dict):
            if idx in obj:
                return obj[idx]
            raise CorpLangRuntimeError(
                f"Key '{idx}' not found in dictionary",
                RuntimeErrorType.REFERENCE_ERROR,
                node=node,
            )

        if isinstance(obj, str):
            if not isinstance(idx, int):
                raise CorpLangRuntimeError(
                    f"String index must be integer, got {type(idx).__name__}",
                    RuntimeErrorType.TYPE_ERROR,
                    node=node,
                )
            if idx < 0 or idx >= len(obj):
                raise CorpLangRuntimeError(
                    f"String index {idx} out of range",
                    RuntimeErrorType.TYPE_ERROR,
                    node=node,
                )
            return obj[idx]

        if hasattr(obj, "__getitem__"):
            try:
                return obj[idx]
            except Exception:
                pass

        if isinstance(obj, InstanceObject):
            # Try Map/List-like helpers exposed via methods
            try:
                getter = obj.get("get")
                if callable(getter):
                    return getter(idx)
            except Exception:
                pass
            try:
                raw_fn = obj.get("__raw__")
                if callable(raw_fn):
                    raw = raw_fn()
                    if isinstance(raw, (list, tuple, dict, str)):
                        if isinstance(raw, dict):
                            if idx in raw:
                                return raw[idx]
                        else:
                            return raw[idx]
            except Exception:
                pass

        raise CorpLangRuntimeError(
            f"Cannot index into {type(obj).__name__}",
            RuntimeErrorType.TYPE_ERROR,
            node=node,
        )


class BinaryExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ in ("BinaryExpression", "BinaryOp") and hasattr(node, "operator")

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        left = resolve_node_value(getattr(node, "left", None), context)
        right = resolve_node_value(getattr(node, "right", None), context)
        op = getattr(node, "operator", None)

        # Guard against None operands to avoid Python TypeError and surface a clearer runtime error.
        # For ordering comparisons, treat missing values as 0 to avoid runtime crashes.
        if op in ("<", "<=", ">", ">=") and (left is None or right is None):
            left = 0 if left is None else left
            right = 0 if right is None else right
        elif op in ("==", "!="):
            # Equality/inequality can safely compare None values without raising.
            pass
        elif left is None or right is None:
            line = getattr(node, "line", None)
            col = getattr(node, "column", None)
            loc = f" (line {line}, col {col})" if line is not None and col is not None else ""
            node_name = type(node).__name__
            left_ast = type(getattr(node, "left", None)).__name__
            right_ast = type(getattr(node, "right", None)).__name__
            left_name = getattr(getattr(node, "left", None), "name", None)
            right_name = getattr(getattr(node, "right", None), "property", None)
            raise CorpLangRuntimeError(
                f"Cannot apply operator '{op}' to {type(left).__name__} and {type(right).__name__}{loc} [node={node_name} left_ast={left_ast} right_ast={right_ast} left={left_name} right={right_name}]",
                RuntimeErrorType.TYPE_ERROR,
            )
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise CorpLangRuntimeError("Division by zero", RuntimeErrorType.TYPE_ERROR)
            return left / right
        if op == "%":
            return left % right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op in ("in", "not in"):
            # Membership support for common containers and Map-like objects
            contains = False
            try:
                if isinstance(right, dict):
                    contains = left in right
                elif hasattr(right, "has") and callable(getattr(right, "has", None)):
                    contains = bool(right.has(left))
                elif isinstance(right, (list, tuple, set, str)):
                    contains = left in right
                elif hasattr(right, "__contains__"):
                    contains = left in right
            except Exception:
                contains = False
            return contains if op == "in" else (not contains)
        if op in ("&&", "and"):
            return bool(left) and bool(right)
        if op in ("||", "or"):
            return bool(left) or bool(right)
        raise CorpLangRuntimeError(f"Unknown binary operator: {op}", RuntimeErrorType.SYNTAX_ERROR)


class TernaryExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "Ternary"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        condition = resolve_node_value(getattr(node, "condition", None), context)
        branch = "true_expr" if condition else "false_expr"
        chosen = getattr(node, branch, None)
        return resolve_node_value(chosen, context)


class UnaryExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ in ("UnaryExpression", "UnaryOp") and hasattr(node, "operator")

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        operand = resolve_node_value(getattr(node, "operand", None), context)
        op = getattr(node, "operator", None)
        if op in ("!", "not"):
            return not bool(operand)
        if op == "-":
            if isinstance(operand, (int, float)):
                return -operand
            raise CorpLangRuntimeError(
                f"Unary minus requires number, got {type(operand).__name__}",
                RuntimeErrorType.TYPE_ERROR,
            )
        if op == "+":
            if isinstance(operand, (int, float)):
                return +operand
            raise CorpLangRuntimeError(
                f"Unary plus requires number, got {type(operand).__name__}",
                RuntimeErrorType.TYPE_ERROR,
            )
        raise CorpLangRuntimeError(f"Unknown unary operator: {op}", RuntimeErrorType.SYNTAX_ERROR)


class GenericIdentifierExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "GenericIdentifier"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        name = getattr(node, "name", None)
        if not isinstance(name, str) or not name:
            raise CorpLangRuntimeError(
                f"GenericIdentifier node missing valid name: {name}",
                RuntimeErrorType.REFERENCE_ERROR,
            )
        try:
            return context.get_var(name)
        except CorpLangRuntimeError:
            if name == "Dict":

                class DictWrap(dict):
                    def set(self, k, v):
                        self[k] = v

                    def get(self, k, default=None):
                        return self[k] if k in self else default

                    @property
                    def length(self):
                        return len(self)

                def new_dict():
                    return DictWrap()

                return new_dict
            if name == "List":

                class ListWrap(list):
                    def append(self, v):
                        super().append(v)

                    @property
                    def length(self):
                        return len(self)

                    def extend(self, other):
                        super().extend(other)

                def new_list():
                    return ListWrap()

                return new_list
            raise


class JsonObjectExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "JsonObject"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Get the raw value dict from the AST node
        raw_value = getattr(node, "value", {}) or {}

        # If it's already a plain dict with no AST nodes, return it
        if not raw_value:
            return {}

        # Evaluate each value in the dict to resolve variables, expressions, etc.
        evaluated_dict = {}
        for key, value in raw_value.items():
            # If the value is an AST node, evaluate it
            if hasattr(value, "__class__") and hasattr(value.__class__, "__name__"):
                node_type = value.__class__.__name__
                # Check if it's an AST node (has typical AST attributes)
                if hasattr(value, "line") or node_type in (
                    "Identifier",
                    "Literal",
                    "BinaryOp",
                    "JsonObject",
                    "JsonArray",
                    "CallExpression",
                ):
                    evaluated_dict[key] = context.interpreter.execute(value, context)
                else:
                    # It's a regular Python object
                    evaluated_dict[key] = value
            else:
                # Plain value (string, number, etc.)
                evaluated_dict[key] = value

        return evaluated_dict


class JsonArrayExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "JsonArray"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Get the raw value list from the AST node
        raw_value = getattr(node, "value", []) or []

        # If it's already a plain list with no AST nodes, return it
        if not raw_value:
            return []

        # Evaluate each item in the list to resolve variables, expressions, etc.
        evaluated_list = []
        for item in raw_value:
            # If the item is an AST node, evaluate it
            if hasattr(item, "__class__") and hasattr(item.__class__, "__name__"):
                node_type = item.__class__.__name__
                # Check if it's an AST node
                if hasattr(item, "line") or node_type in (
                    "Identifier",
                    "Literal",
                    "BinaryOp",
                    "JsonObject",
                    "JsonArray",
                    "CallExpression",
                ):
                    evaluated_list.append(context.interpreter.execute(item, context))
                else:
                    # It's a regular Python object
                    evaluated_list.append(item)
            else:
                # Plain value
                evaluated_list.append(item)

        return evaluated_list


class InterpolatedStringExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "InterpolatedString" and hasattr(node, "parts")

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        parts: List[Any] = getattr(node, "parts", []) or []
        result: List[str] = []

        for part in parts:
            # Static string portion
            if isinstance(part, str):
                result.append(part)
                continue

            # Tuple from parser: (expr_node, fmt_spec, conv)
            expr_node: Any = None
            fmt_spec: Optional[str] = None
            conv: Optional[str] = None
            if isinstance(part, tuple) and part:
                expr_node = part[0]
                if len(part) > 1:
                    fmt_spec = part[1]
                if len(part) > 2:
                    conv = part[2]
            else:
                expr_node = part

            try:
                value = resolve_node_value(expr_node, context)
            except Exception:
                # Propagate runtime errors to the interpreter to keep stack traces
                raise

            # If the evaluated expression is an awaitable returned by an async method,
            # attempt to await it synchronously so f-strings include resolved values.
            try:
                import inspect
                if inspect.isawaitable(value) or (hasattr(value, "__await__") and callable(getattr(value, "__await__", None))):
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if not loop.is_running():
                            async def _runner(v):
                                return await v

                            value = asyncio.run(_runner(value))
                        else:
                            # Drive generator returned by __await__ synchronously
                            aw = value.__await__()
                            try:
                                nxt = next(aw)
                                while True:
                                    nxt = aw.send(nxt)
                            except StopIteration as st:
                                value = st.value
                    except Exception:
                        # Propagate awaiting errors so try/catch in MP works
                        raise

            except Exception:
                raise

            try:
                val_to_format = repr(value) if conv == "r" else value
                if fmt_spec:
                    try:
                        result.append(format(val_to_format, fmt_spec))
                    except Exception:
                        result.append(str(val_to_format))
                else:
                    result.append(str(val_to_format))
            except Exception:
                result.append(str(value))

        return "".join(result)


def register(registry: ExecutorRegistry):
    from src.corplang.compiler.nodes import (
        Literal,
        NullLiteral,
        Identifier,
        IndexAccess,
        BinaryOp,
        Ternary,
        UnaryOp,
        GenericIdentifier,
        JsonObject,
        JsonArray,
        InterpolatedString,
    )

    registry.register(Literal, LiteralExecutor())
    registry.register(NullLiteral, NullLiteralExecutor())
    registry.register(Identifier, IdentifierExecutor())
    registry.register(IndexAccess, IndexAccessExecutor())
    registry.register(BinaryOp, BinaryExecutor())
    registry.register(Ternary, TernaryExecutor())
    registry.register(UnaryOp, UnaryExecutor())
    registry.register(GenericIdentifier, GenericIdentifierExecutor())
    registry.register(JsonObject, JsonObjectExecutor())
    registry.register(JsonArray, JsonArrayExecutor())
    registry.register(InterpolatedString, InterpolatedStringExecutor())
