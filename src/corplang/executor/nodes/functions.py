"""Function-related node executors for the CorpLang interpreter.

This module provides executors for function declarations, calls, lambdas and
async intents. Keep imports minimal and local imports only when necessary to
avoid import cycles.
"""

from __future__ import annotations

from typing import Any

from src.corplang.executor.node import NodeExecutor
from src.corplang.executor.context import ExecutionContext
from src.corplang.executor.helpers import get_node_attr, resolve_node_value
from src.corplang.executor.interpreter import ExecutorRegistry
from src.corplang.executor.objects import CorpLangFunction
from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType


class FunctionDeclarationExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "FunctionDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        fn = CorpLangFunction(node, context.environment, context.interpreter)
        name = getattr(node, "name", None)
        if not name:
            raise CorpLangRuntimeError(
                "FunctionDeclaration missing name", RuntimeErrorType.SYNTAX_ERROR
            )
        context.define_var(name, fn, "function")

        return node


class FunctionCallExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "FunctionCall"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        callee_node = get_node_attr(node, "callee", "func", "name")
        if isinstance(callee_node, str):
            func = context.get_var(callee_node)
        else:
            # If calling a property (e.g., this.nome()), prefer method lookup on instances
            # so methods with the same name as fields are callable via `this.nome()`.
            try:
                if getattr(callee_node, "__class__", None) and getattr(callee_node, "__class__", None).__name__ == "PropertyAccess":
                    obj_node = getattr(callee_node, "obj", None) or getattr(callee_node, "object", None)
                    prop_name = getattr(callee_node, "prop", None) or getattr(callee_node, "property", None)
                    obj_val = resolve_node_value(obj_node, context)
                    try:
                        from src.corplang.executor.objects import InstanceObject

                        if isinstance(obj_val, InstanceObject):
                            # Prefer method wrapper when present (even if a field exists)
                            try:
                                func = obj_val.get_method(prop_name, context=context)
                            except Exception:
                                func = obj_val.get(prop_name, context=context)
                        else:
                            func = resolve_node_value(callee_node, context)
                    except Exception:
                        func = resolve_node_value(callee_node, context)
                else:
                    func = resolve_node_value(callee_node, context)
            except Exception:
                # Fall back to general resolution and let errors propagate
                func = resolve_node_value(callee_node, context)
        # callee resolved; metadata extraction suppressed in non-debug mode
        pass
        args_list = get_node_attr(node, "args", "arguments", default=[]) or []
        positional = []
        keyword = {}
        for arg in args_list:
            name = getattr(arg, "name", None)
            value_node = getattr(arg, "value", arg)
            value = resolve_node_value(value_node, context)
            if name:
                if name in keyword:
                    raise CorpLangRuntimeError(
                        f"Argument '{name}' specified multiple times",
                        RuntimeErrorType.TYPE_ERROR,
                        node=node,
                        suggestions=["Remove duplicate named arguments"],
                    )
                keyword[name] = value
            else:
                positional.append(value)

        # Prevent calling async CorpLang functions from non-async contexts without await
        is_corplang_fn = getattr(func, "__class__", None) and hasattr(func, "declaration")
        is_async_decl = False
        if is_corplang_fn:
            is_async_decl = bool(getattr(getattr(func, "declaration", None), "is_async", False))
            if is_async_decl:
                # allowed if current context is async or if we're inside an Await evaluation
                if not getattr(context, "is_async", False) and not getattr(context, "_awaiting", False):
                    raise CorpLangRuntimeError(
                        f"Cannot call async function '{getattr(func.declaration, 'name', '<anon>')}' from non-async context; use 'await' or mark caller async",
                        RuntimeErrorType.TYPE_ERROR,
                        node=node,
                    )

        # Support method wrappers created by InstanceObject.get (annotated with _is_corplang_method)
        if getattr(func, "_is_corplang_method", False):
            decl = getattr(func, "_declare", None)
            if decl and getattr(decl, "is_async", False):
                if not getattr(context, "is_async", False) and not getattr(context, "_awaiting", False):
                    raise CorpLangRuntimeError(
                        f"Cannot call async method '{getattr(decl, 'name', '<anon>')}' from non-async context; use 'await' or mark caller async",
                        RuntimeErrorType.TYPE_ERROR,
                        node=node,
                    )


        # For CorpLang functions / methods, pass the call context explicitly
        # as a reserved kwarg so method wrappers receive a real ExecutionContext.
        injected_call_context = False
        if getattr(func, "_is_corplang_method", False) and "_call_context" not in keyword:
            keyword["_call_context"] = context
            injected_call_context = True

        result = None
        try:
            if callable(func) or hasattr(func, "__call__"):
                result = func(*positional, **keyword)
            else:
                # Calling a non-callable should raise a runtime error (not silently return None)
                try:
                    from src.corplang.tools.diagnostics import _safe_repr
                    func_repr = _safe_repr(func)
                except Exception:
                    func_repr = "<unrepresentable>"
                raise CorpLangRuntimeError(f"Not a function: {func_repr}", RuntimeErrorType.TYPE_ERROR, node=node)

            return result
        finally:
            if injected_call_context:
                try:
                    keyword.pop("_call_context", None)
                except Exception:
                    pass
        try:
            from src.corplang.tools.diagnostics import _safe_repr
            func_repr = _safe_repr(func)
        except Exception:
            func_repr = "<unrepresentable>"
        raise CorpLangRuntimeError(f"Not a function: {func_repr}", RuntimeErrorType.TYPE_ERROR)


class LambdaExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "LambdaExpression"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        return CorpLangFunction(node, context.environment, context.interpreter)


class AwaitExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ in ("AwaitExpression", "Await")

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Mark context as awaiting so inner function calls can know they're being awaited
        prev = getattr(context, "_awaiting", False)
        context._awaiting = True
        try:
            val = resolve_node_value(get_node_attr(node, "expression", "argument"), context)
        finally:
            context._awaiting = prev

        try:
            import inspect

            # Debug info to help diagnose awaitable objects in f-strings and method calls
            # Diagnostic logging
            try:
                try:
                    is_a = inspect.isawaitable(val)
                except Exception:
                    is_a = False
                has_await = hasattr(val, "__await__") and callable(getattr(val, "__await__", None))

            except Exception:
                pass

            is_awaitable = (inspect.isawaitable(val) or (hasattr(val, "__await__") and callable(getattr(val, "__await__", None))))
            if is_awaitable:
                import asyncio

                async def _runner(v):
                    return await v

                # Prefer asyncio.run when event loop is not running; otherwise
                # execute the awaitable by driving its __await__ generator synchronously.
                try:
                    loop = asyncio.get_event_loop()
                    if not loop.is_running():
                        return asyncio.run(_runner(val))
                except Exception:
                    # fallback to manual runner
                    pass

                # Manual synchronous driver for generator-based awaitables
                aw = val.__await__()
                try:
                    nxt = next(aw)
                    while True:
                        nxt = aw.send(nxt)
                except StopIteration as st:
                    return st.value
                except Exception:
                    # propagate error so `try/catch` in MP can handle it
                    raise
        except Exception:
            pass
        return val


class AsyncIntentExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "AsyncIntentDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        name = getattr(node, "name", None)
        if not name:
            raise CorpLangRuntimeError(
                "AsyncIntentDeclaration missing name", RuntimeErrorType.SYNTAX_ERROR
            )
        context.define_var(name, node, "async_function")
        return node


def register(registry: ExecutorRegistry):
    from src.corplang.compiler.nodes import (
        FunctionDeclaration,
        FunctionCall,
        LambdaExpression,
        Await,
    )

    registry.register(FunctionDeclaration, FunctionDeclarationExecutor())
    registry.register(FunctionCall, FunctionCallExecutor())
    registry.register(LambdaExpression, LambdaExecutor())
    registry.register(Await, AwaitExecutor())
