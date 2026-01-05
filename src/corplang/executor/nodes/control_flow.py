from __future__ import annotations

from typing import Any, Iterable, List
import inspect
import asyncio

from src.corplang.executor.node import NodeExecutor
from src.corplang.executor.context import ExecutionContext
from src.corplang.executor.helpers import get_node_attr, resolve_node_value
from src.corplang.executor.interpreter import ExecutorRegistry
from src.corplang.core.exceptions import CorpLangRuntimeError, CorpLangRaisedException, RuntimeErrorType, ReturnException, BreakException, ContinueException
from src.corplang.executor.objects import InstanceObject
from src.corplang.tools import diagnostics


def _iterable_from_value(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, (list, tuple)):
        return value
    try:
        return list(value)
    except Exception:
        raise CorpLangRuntimeError(
            f"Object of type {type(value)} is not iterable", RuntimeErrorType.TYPE_ERROR
        )


def _iterate_with_protocol(iterator: InstanceObject, node: Any, context: ExecutionContext) -> Any:
    """Execute iteration using Iterable/Iterator protocol."""
    result = None
    var_name = getattr(node, "variable", None)
    
    while True:
        # Call hasNext()
        has_next_method = iterator.get("hasNext")
        if not callable(has_next_method):
            raise CorpLangRuntimeError(
                "Iterator missing hasNext() method",
                RuntimeErrorType.TYPE_ERROR
            )
        has_next = has_next_method()
        
        if not has_next:
            break
        
        # Call next()
        next_method = iterator.get("next")
        if not callable(next_method):
            raise CorpLangRuntimeError(
                "Iterator missing next() method",
                RuntimeErrorType.TYPE_ERROR
            )
        item = next_method()
        
        # Execute loop body
        try:
            child = context.child({var_name: item} if var_name else None)
            result = context.interpreter.execute(get_node_attr(node, "body"), child)
        except BreakException:
            break
        except ContinueException:
            continue
    
    return result


class IfExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "IfStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        condition_node = get_node_attr(node, "condition", "test")
        condition = resolve_node_value(condition_node, context)
        if condition:
            return context.interpreter.execute(
                get_node_attr(node, "then_stmt", "consequent"), context
            )
        alt = get_node_attr(node, "else_stmt", "alternate")
        if alt:
            return context.interpreter.execute(alt, context)
        return None


class WhileExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "WhileStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        result = None
        while resolve_node_value(get_node_attr(node, "condition", "test"), context):
            try:
                result = context.interpreter.execute(get_node_attr(node, "body"), context)
            except BreakException:
                break
            except ContinueException:
                continue
        return result


class ForExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ForStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        result = None
        if get_node_attr(node, "init"):
            context.interpreter.execute(node.init, context)
        while True:
            condition_node = get_node_attr(node, "condition")
            if condition_node and not resolve_node_value(condition_node, context):
                break
            try:
                result = context.interpreter.execute(get_node_attr(node, "body"), context)
            except BreakException:
                break
            except ContinueException:
                pass  # Continue to update
            if get_node_attr(node, "update"):
                context.interpreter.execute(node.update, context)
        return result


class ForInExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ForInStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        iterable_value = resolve_node_value(get_node_attr(node, "iterable", "iterable"), context)
        result = None
        
        # 1. Try explicit iteration protocol (__iter__)
        if isinstance(iterable_value, InstanceObject):
            iter_method = None
            try:
                iter_method = iterable_value.get("__iter__")
            except (KeyError, AttributeError):
                iter_method = None
            
            if iter_method and callable(iter_method):
                iterator = iter_method()
                result = _iterate_with_protocol(iterator, node, context)
                return result
            
            # Legacy fallback: __raw__
            try:
                raw_getter = iterable_value.get("__raw__")
                if callable(raw_getter):
                    raw_data = raw_getter()
                    if isinstance(raw_data, dict):
                        iterable = list(raw_data.keys())
                    else:
                        iterable = list(raw_data)
                else:
                    raise CorpLangRuntimeError(
                        f"Object {iterable_value} is not iterable (missing __iter__ or __raw__)",
                        RuntimeErrorType.TYPE_ERROR,
                    )
            except (KeyError, AttributeError):
                raise CorpLangRuntimeError(
                    f"Object {iterable_value} is not iterable", RuntimeErrorType.TYPE_ERROR
                )
        # 2. Fallback for native types
        elif isinstance(iterable_value, dict):
            iterable = list(iterable_value.keys())
        elif isinstance(iterable_value, (list, tuple)):
            iterable = list(iterable_value)
        else:
            iterable = list(_iterable_from_value(iterable_value))
        
        # 3. Execute loop body
        var_name = getattr(node, "variable", None)
        for item in iterable:
            try:
                child = context.child({var_name: item} if var_name else None)
                result = context.interpreter.execute(get_node_attr(node, "body"), child)
            except BreakException:
                break
            except ContinueException:
                continue
        return result


class ForOfExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ForOfStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        iterable_value = resolve_node_value(get_node_attr(node, "iterable", "iterable"), context)
        result = None
        
        # 1. Try explicit iteration protocol (__iter__)
        if isinstance(iterable_value, InstanceObject):
            iter_method = None
            try:
                iter_method = iterable_value.get("__iter__")
            except (KeyError, AttributeError):
                iter_method = None
            
            if iter_method and callable(iter_method):
                # Use same protocol iteration as ForIn
                return self._iterate_protocol(iter_method(), node, context)
            
            # Legacy fallback: __raw__
            try:
                raw_getter = iterable_value.get("__raw__")
                if callable(raw_getter):
                    raw_data = raw_getter()
                    if isinstance(raw_data, dict):
                        iterable = list(raw_data.values())
                    else:
                        iterable = list(raw_data)
                else:
                    raise CorpLangRuntimeError(
                        f"Object {iterable_value} is not iterable (missing __iter__ or __raw__)",
                        RuntimeErrorType.TYPE_ERROR,
                    )
            except (KeyError, AttributeError):
                raise CorpLangRuntimeError(
                    f"Object {iterable_value} is not iterable", RuntimeErrorType.TYPE_ERROR
                )
        # 2. Fallback for native types
        elif isinstance(iterable_value, dict):
            iterable = list(iterable_value.values())
        else:
            iterable = list(_iterable_from_value(iterable_value))
        
        # 3. Execute loop body
        var_name = getattr(node, "variable", None)
        for item in iterable:
            try:
                child = context.child({var_name: item} if var_name else None)
                result = context.interpreter.execute(get_node_attr(node, "body"), child)
            except BreakException:
                break
            except ContinueException:
                continue
        return result


class ThrowExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ThrowStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        if getattr(node, "expression", None):
            value = resolve_node_value(node.expression, context)
            # Preserve original object so TryExecutor can wrap with diagnostics
            raise CorpLangRaisedException(value)
        raise CorpLangRaisedException("Unknown error")


class TryExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "TryStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        from src.corplang.core.exceptions import ReturnException

        return_from_try = None
        has_return_from_try = False

        try:
            try_block = get_node_attr(node, "try_block", "block") or []
            result = None
            for stmt in try_block:
                result = context.interpreter.execute(stmt, context)
            return_from_try = result
        except ReturnException as ret:
            # Return statement happened in try block - save it to propagate after finally
            return_from_try = ret.value
            has_return_from_try = True
        except Exception as exc:
            has_return_from_try = False

            def _ensure_exception_classes():
                try:
                    exports = context.interpreter._import_module("core.lang.exceptions", context.current_file)
                    ge = getattr(context.interpreter, "global_env", None)
                    if ge and isinstance(exports, dict):
                        for k, v in exports.items():
                            if k in ("Exception", "Error", "RuntimeError", "TypeError", "GenericContractError", "RuntimeException"):
                                try:
                                    ge.define(k, v, "class")
                                except Exception:
                                    try:
                                        ge.variables[k] = v
                                    except Exception:
                                        pass
                except Exception:
                    pass

            def _resolve_class(name: str):
                ge = getattr(context.interpreter, "global_env", None)
                if ge and name in getattr(ge, "variables", {}):
                    val = ge.variables.get(name)
                    if hasattr(val, "instance_methods") or hasattr(val, "name"):
                        return val
                return None

            def _make_lang_exception(name: str, message: str):
                cls = _resolve_class(name) or _resolve_class("Exception")
                if cls is None:
                    return None

                # Never let constructor failures cascade back into the handler
                try:
                    return cls(message)
                except Exception:
                    try:
                        return cls()
                    except Exception:
                        # Final fallback: return a plain payload so we don't re-enter error normalization
                        return {"name": name, "message": message}

            def _has_payload_stacktrace(payload: Any) -> bool:
                try:
                    if isinstance(payload, InstanceObject):
                        fields = getattr(payload, "_fields", {})
                        if fields.get("stacktrace"):
                            return True
                    elif isinstance(payload, dict):
                        if payload.get("stacktrace"):
                            return True
                    elif hasattr(payload, "stacktrace"):
                        if getattr(payload, "stacktrace", None):
                            return True
                except Exception:
                    pass
                return False

            def _effective_frames(exc_obj: Exception, payload: Any) -> list:
                try:
                    existing = getattr(exc_obj, "mp_stack", None)
                    if existing:
                        return list(existing)
                except Exception:
                    pass

                try:
                    if isinstance(payload, InstanceObject):
                        fields = getattr(payload, "_fields", {})
                        if fields.get("stacktrace"):
                            return fields.get("stacktrace")
                    elif isinstance(payload, dict):
                        if payload.get("stacktrace"):
                            return payload.get("stacktrace")
                    elif hasattr(payload, "stacktrace"):
                        st = getattr(payload, "stacktrace", None)
                        if st:
                            return st
                except Exception:
                    pass

                try:
                    return context.interpreter._snapshot_call_stack()
                except Exception:
                    pass

                try:
                    return list(getattr(context.interpreter, "call_stack", []) or [])
                except Exception:
                    return []

            def _attach_stack(payload: Any, frames: list):
                if payload is None or _has_payload_stacktrace(payload):
                    return
                try:
                    if isinstance(payload, InstanceObject):
                        payload.set("stacktrace", frames)
                    elif isinstance(payload, dict):
                        payload["stacktrace"] = frames
                    elif hasattr(payload, "stacktrace"):
                        setattr(payload, "stacktrace", frames)
                except Exception:
                    pass

            def _normalize_exception(exc_obj: Exception):
                try:
                    if isinstance(exc_obj, CorpLangRaisedException):
                        payload = exc_obj.value
                    elif isinstance(exc_obj, CorpLangRuntimeError):
                        payload = getattr(exc_obj, "mp_exception", None)
                        if payload is None:
                            try:
                                msg_val = getattr(exc_obj, "message", None) or str(exc_obj)
                            except Exception:
                                msg_val = str(exc_obj)
                            payload = _make_lang_exception("RuntimeError", msg_val) or exc_obj
                    else:
                        try:
                            from src.corplang.tools.diagnostics import safe_message
                            msg_val = safe_message(exc_obj)
                        except Exception:
                            msg_val = str(exc_obj)
                        payload = _make_lang_exception("RuntimeError", msg_val) or exc_obj

                    frames = _effective_frames(exc_obj, payload)
                    try:
                        if getattr(exc_obj, "mp_stack", None) in (None, []):
                            setattr(exc_obj, "mp_stack", frames)
                    except Exception:
                        pass
                    _attach_stack(payload, frames)
                    return payload
                except Exception:
                    # As a last resort, propagate the original object to avoid infinite recursion
                    return exc_obj

            def _matches(expected, obj):
                from src.corplang.executor.type_system import ensure_type_object, type_from_annotation, type_from_value
                try:
                    expected_type = None
                    try:
                        from src.corplang.compiler.nodes import TypeAnnotation
                        if isinstance(expected, TypeAnnotation):
                            expected_type = type_from_annotation(expected, context.interpreter)
                    except Exception:
                        expected_type = None
                    if expected_type is None:
                        expected_type = ensure_type_object(expected, context.interpreter)
                    actual_type = type_from_value(obj, context.interpreter)
                    if expected_type is None or actual_type is None:
                        return False
                    return actual_type.is_assignable_to(expected_type)
                except Exception:
                    return False

            _ensure_exception_classes()
            mp_obj = _normalize_exception(exc)

            handled = False
            for catch in get_node_attr(node, "catch_clauses", "handler", "catch") or []:
                child = context.child()
                exc_var = getattr(catch, "exception_var", None) or getattr(catch, "param", None)
                expected_type = getattr(catch, "exception_type", None)

                if expected_type is None:
                    continue

                if not _matches(expected_type, mp_obj):
                    continue

                if exc_var:
                    try:
                        child.define_var(exc_var, mp_obj, "object")
                    except Exception:
                        try:
                            child.define_var(exc_var, mp_obj, None)
                        except Exception:
                            child.define_var(exc_var, str(mp_obj), "string")

                result = None
                try:
                    for stmt in getattr(catch, "body", []) or []:
                        result = context.interpreter.execute(stmt, child)
                    return_from_try = result
                except ReturnException as ret:
                    return_from_try = ret.value
                    has_return_from_try = True
                handled = True
                break

            if not handled:
                raise CorpLangRaisedException(mp_obj)

        # Execute finally block (ALWAYS execute, regardless of return or exception)
        finally_block = get_node_attr(node, "finally_block", "finalizer")
        finally_returned = False
        finally_return_value = None

        if finally_block:
            try:
                for stmt in finally_block:
                    context.interpreter.execute(stmt, context)
            except ReturnException as ret:
                # Finally has its own return, it takes precedence
                finally_returned = True
                finally_return_value = ret.value

        # After finally executes, decide what to do:
        if finally_returned:
            # Finally had a return, propagate it
            raise ReturnException(finally_return_value)
        elif has_return_from_try:
            # Try or catch had a return, and finally didn't override it
            raise ReturnException(return_from_try)

        return None


# Register function moved to bottom of file to ensure classes are defined before registration


class WithExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "WithStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        items = get_node_attr(node, "items", "managers") or []
        managers: List[Any] = []
        enter_results: List[Any] = []
        is_async = getattr(node, "is_async", False)

        # Evaluate managers left-to-right
        for item in items:
            mgr_val = resolve_node_value(
                get_node_attr(item, "context_expr", "context_expr"), context
            )
            managers.append(mgr_val)

        child = context.child()

        try:
            # Call enter on each manager and bind targets
            for i, item in enumerate(items):
                mgr = managers[i]
                enter_val = None
                try:
                    if hasattr(mgr, "get"):
                        # InstanceObject
                        try:
                            enter_callable = mgr.get("__enter__")
                        except Exception:
                            enter_callable = None
                    else:
                        enter_callable = getattr(mgr, "__enter__", None) or getattr(
                            mgr, "enter", None
                        )

                    if callable(enter_callable):
                        ret = enter_callable()
                        if is_async and inspect.isawaitable(ret):
                            # run awaitable to completion (bridge to Python async)
                            enter_val = asyncio.run(ret)
                        else:
                            enter_val = ret
                    else:
                        enter_val = mgr
                except Exception as e:
                    raise CorpLangRaisedException(e)

                enter_results.append(enter_val)
                target = getattr(item, "target", None)
                if target:
                    child.define_var(target, enter_val)

            # Execute body in child context
            return context.interpreter.execute(get_node_attr(node, "body"), child)

        except CorpLangRaisedException as exc:
            # On exception, call exit on managers in reverse order
            suppressed = False
            for mgr in reversed(managers):
                try:
                    if hasattr(mgr, "get"):
                        try:
                            exit_callable = mgr.get("__exit__")
                        except Exception:
                            exit_callable = None
                    else:
                        exit_callable = getattr(mgr, "__exit__", None) or getattr(mgr, "exit", None)
                    if callable(exit_callable):
                        res = exit_callable(type(exc), exc, None)
                        if is_async and inspect.isawaitable(res):
                            try:
                                res = asyncio.run(res)
                            except Exception:
                                res = False
                        if res:
                            suppressed = True
                except Exception:
                    # ignore errors in exit
                    pass
            if suppressed:
                return None
            raise
        finally:
            # Ensure exit called if no exception
            if "exc" not in locals():
                for mgr in reversed(managers):
                    try:
                        if hasattr(mgr, "get"):
                            try:
                                exit_callable = mgr.get("__exit__")
                            except Exception:
                                exit_callable = None
                        else:
                            exit_callable = getattr(mgr, "__exit__", None) or getattr(
                                mgr, "exit", None
                            )
                        if callable(exit_callable):
                            try:
                                res = exit_callable(None, None, None)
                                if is_async and inspect.isawaitable(res):
                                    try:
                                        asyncio.run(res)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                    except Exception:
                        pass


class BreakExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "BreakStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        raise BreakException()


class ContinueExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ContinueStatement"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        raise ContinueException()


def register(registry: ExecutorRegistry):
    """Register control-flow related executors with the given registry."""
    from src.corplang.compiler.nodes import (
        IfStatement,
        WhileStatement,
        ForStatement,
        ForInStatement,
        ForOfStatement,
        ThrowStatement,
        TryStatement,
        WithStatement,
        BreakStatement,
        ContinueStatement,
    )

    registry.register(IfStatement, IfExecutor())
    registry.register(WhileStatement, WhileExecutor())
    registry.register(ForStatement, ForExecutor())
    registry.register(ForInStatement, ForInExecutor())
    registry.register(ForOfStatement, ForOfExecutor())
    registry.register(ThrowStatement, ThrowExecutor())
    registry.register(TryStatement, TryExecutor())
    registry.register(WithStatement, WithExecutor())
    registry.register(BreakStatement, BreakExecutor())
    registry.register(ContinueStatement, ContinueExecutor())
