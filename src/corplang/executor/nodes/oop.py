"""Object-oriented node executors (classes, property access, 'this', 'super').

This module focuses on class and instance semantics required by the runtime.
"""

from __future__ import annotations

import time
from typing import Any

from src.corplang.executor.node import NodeExecutor
from src.corplang.executor.context import ExecutionContext
from src.corplang.executor.helpers import get_node_attr, resolve_node_value
from src.corplang.executor.interpreter import ExecutorRegistry
from src.corplang.executor.objects import ClassObject, InstanceObject
from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType, ReturnException
# CorpLangList removed; use native Python lists
from src.corplang.executor.context import Environment
from src.corplang.core.utils import bind_arguments_to_params as _bind_arguments_to_params, bind_and_exec


class ClassDeclarationExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ClassDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        name = getattr(node, "name", None)
        if not name:
            raise CorpLangRuntimeError(
                "ClassDeclaration missing name", RuntimeErrorType.SYNTAX_ERROR
            )
        # Pre-bind class symbol to allow self-references during class object construction
        try:
            context.define_var(name, None, "class")
        except Exception:
            pass
        # Ensure AST node has file attribute set for diagnostics
        try:
            if getattr(node, "file", None) is None:
                node.file = context.current_file or getattr(
                    context.interpreter, "current_file", None
                )
        except Exception:
            pass
        cls_obj = ClassObject(node, context.interpreter, context.environment)
        context.define_var(name, cls_obj, "class")

        # If class is flagged as driver, register minimal metadata
        if getattr(node, "is_driver", False):
            required = {"connect", "disconnect", "execute", "query", "transaction"}
            method_names = {
                getattr(m, "name", None)
                for m in getattr(node, "body", [])
                if getattr(m, "name", None)
            }
            missing = sorted(required - method_names)
            if missing:
                raise CorpLangRuntimeError(
                    f"Driver '{name}' missing required methods: {', '.join(missing)}",
                    RuntimeErrorType.TYPE_ERROR,
                    node=node,
                )
            registry = getattr(context.interpreter, "driver_registry", None)
            if registry is not None:
                registry[name] = {
                    "class": cls_obj,
                    "methods": method_names,
                    "file": getattr(node, "file", None) or getattr(node, "file_path", None),
                    "line": getattr(node, "line", None),
                    "column": getattr(node, "column", None),
                    "extends": getattr(node, "extends", None),
                    "implements": getattr(node, "implements", None),
                }
                try:
                    context.define_var("__drivers__", registry, "registry")
                except Exception:
                    pass
        return node


class InterfaceDeclarationExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "InterfaceDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        name = getattr(node, "name", None)
        if not name:
            raise CorpLangRuntimeError(
                "InterfaceDeclaration missing name", RuntimeErrorType.SYNTAX_ERROR
            )
        context.define_var(name, node, "interface")
        return node


class ContractDeclarationExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ContractDeclaration"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        name = getattr(node, "name", None)
        if not name:
            raise CorpLangRuntimeError(
                "ContractDeclaration missing name", RuntimeErrorType.SYNTAX_ERROR
            )
        context.define_var(name, node, "contract")
        return node


class NewExpressionExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "NewExpression"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        class_name = get_node_attr(node, "class_name", "callee")
        if hasattr(class_name, "name"):
            class_name = getattr(class_name, "name")
        
        cls = context.get_var(class_name)
        
        # Extract type_arguments if present
        type_arguments = getattr(node, "type_arguments", None)
        generic_env = {}
        if type_arguments:
            # Build generic_env mapping from type_arguments
            # For now, store as dict { index: TypeAnnotation }
            # ClassObject will need to resolve these against its declared generics
            for idx, type_arg in enumerate(type_arguments):
                generic_env[idx] = type_arg
        
        args_list = getattr(node, "args", None) or getattr(node, "arguments", []) or []
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

        # If cls is a native callable (e.g., ClassObject.__call__ or a Python constructor), invoke it
        if callable(cls):
            # Pass generic_env via keyword argument
            if generic_env:
                keyword['__generic_env__'] = generic_env
            
            instance = cls(*positional, **keyword)
            return instance

        # Support runtime ClassObject-like values
        if hasattr(cls, "instance_methods") or getattr(cls, "name", None):
            if generic_env:
                keyword['__generic_env__'] = generic_env
            instance = cls(*positional, **keyword)
            return instance

        # Not a class-like object
        raise CorpLangRuntimeError(f"Not a class: {class_name}", RuntimeErrorType.TYPE_ERROR)

        # Emit observability event if callback exists
        if context.observability_callback:
            context.observability_callback("object_created", {
                "class_name": class_name,
                "args": positional + list(keyword.values()),
                "timestamp": time.time()
            })

        return instance


class PropertyAccessExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "PropertyAccess"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        def hasModel():
            return getattr(node.obj, "name", "") == "Model"

        obj = resolve_node_value(get_node_attr(node, "obj", "object"), context)
        prop = get_node_attr(node, "prop", "property")
        # debug: log object and property to diagnose call resolution

        if isinstance(obj, dict) and "__dict__" in obj:
            return obj["__dict__"].get(prop)
        if isinstance(obj, dict) and prop in obj:
            return obj[prop]
        if isinstance(obj, dict) and prop not in obj:
            # Convenience helpers on dicts: provide `.get` and others similar to Python
            if prop == "get":
                def _dict_get(key, default=None):
                    try:
                        return obj.get(key, default)
                    except Exception:
                        return default
                return _dict_get
            if prop == "keys":
                def _dict_keys():
                    return list(obj.keys())
                return _dict_keys
            if prop == "values":
                def _dict_values():
                    return list(obj.values())
                return _dict_values
            if prop == "items":
                def _dict_items():
                    return list(obj.items())
                return _dict_items
            # Missing key on dict: return None (convenience for kwargs-like dicts)
            return None
        if isinstance(obj, InstanceObject):
            # Pass context for private member access validation
            return obj.get(prop, context=context)
        if isinstance(obj, ClassObject):
            if hasModel():
                try:
                    dbg_val = obj.get_static(prop)
                    return dbg_val
                except Exception:
                    raise
            return obj.get_static(prop)
        
        # Handle enum types and values
        from src.corplang.runtime.enums import EnumType, EnumValue
        if isinstance(obj, EnumType):
            # Access enum member: UserRole.ADMIN
            return getattr(obj, prop)
        if isinstance(obj, EnumValue):
            # Access enum value properties: .name or .value
            if prop == "name":
                return obj.name
            if prop == "value":
                return obj.value
        
        if isinstance(obj, (list, tuple)) and prop == "length":
            return len(obj)
        if isinstance(obj, dict) and prop == "length":
            return len(obj)

        # Handle string methods specially to ensure proper return types
        if isinstance(obj, str) and prop == "split":

            def string_split(delimiter=None):
                result = obj.split(delimiter)
                return result

            return string_split
        if isinstance(obj, str) and prop == "replace":

            def string_replace(old, new):
                return obj.replace(old, new)

            return string_replace
        if isinstance(obj, str) and prop == "indexOf":

            def string_indexOf(substring):
                try:
                    return obj.index(substring)
                except ValueError:
                    return -1

            return string_indexOf
        if isinstance(obj, str) and prop == "substring":

            def string_substring(start, end=None):
                if end is None:
                    return obj[start:]
                return obj[start:end]

            return string_substring
        if isinstance(obj, str) and prop == "startsWith":

            def string_startsWith(prefix):
                return obj.startswith(prefix)

            return string_startsWith
        if isinstance(obj, str) and prop == "contains":

            def string_contains(substring):
                return substring in obj

            return string_contains

        if hasattr(obj, prop):
            return getattr(obj, prop)
        # Use safe diagnostics stringification to avoid host repr leaking or raising
        try:
            from src.corplang.tools.diagnostics import _safe_repr
            obj_repr = _safe_repr(obj)
        except Exception:
            obj_repr = "<unrepresentable>"
        raise CorpLangRuntimeError(
            f"Property '{prop}' not found on {obj_repr}", RuntimeErrorType.REFERENCE_ERROR
        )


class ThisExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "ThisExpression"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        try:
            return context.get_var("this")
        except Exception:
            return None


class SuperExecutor(NodeExecutor):
    def can_execute(self, node: Any) -> bool:
        return type(node).__name__ == "SuperExpression"

    def execute(self, node: Any, context: ExecutionContext) -> Any:
        # Return a callable that invokes the parent constructor bound to current instance
        interpreter = context.interpreter

        def super_call(*args, **kwargs):
            try:
                this = context.get_var("this")
            except Exception:
                raise CorpLangRuntimeError(
                    "'super' used outside of class context", RuntimeErrorType.TYPE_ERROR, node=node
                )

            # Resolve current class from scope owner first, then from instance
            cls_obj = None
            owner = getattr(context, "current_scope_owner", None)
            if owner:
                try:
                    cls_obj = context.get_var(owner)
                except Exception:
                    cls_obj = None
            if cls_obj is None:
                try:
                    cls_obj = getattr(this, "class_obj", None)
                except Exception:
                    cls_obj = None

            parent: ClassObject = getattr(cls_obj, "parent", None)
            if not isinstance(parent, ClassObject):
                # No parent or not a valid class object; super() is a no-op
                return None

            # Fetch parent's constructor declaration
            mdecl = (getattr(parent, "instance_methods", {}) or {}).get("constructor")
            if mdecl is None:
                # Parent has no constructor; no-op
                return None

            # Bind parameters
            params = getattr(mdecl, "params", []) or []
            pdefaults = getattr(mdecl, "param_defaults", None) or {}
            bound = _bind_arguments_to_params(
                params,
                pdefaults,
                list(args),
                dict(kwargs or {}),
                interpreter,
                mdecl,
            )

            # Use bind_and_exec to handle parent constructor with proper closure
            # Parent's class environment is used as closure
            closure_env = getattr(parent, '_env', None) or interpreter.global_env
            try:
                # Bind by param name to avoid positional drift and ensure defaults apply
                return bind_and_exec(
                    interpreter,
                    mdecl,
                    closure_env,
                    [],
                    bound,
                    context,
                    this=this,
                    class_ref=parent,
                )
            except ReturnException as ret:
                # Constructors typically return None, but propagate if provided
                return ret.value

        return super_call


def register(registry: ExecutorRegistry):
    from src.corplang.compiler.nodes import (
        ClassDeclaration,
        InterfaceDeclaration,
        ContractDeclaration,
        NewExpression,
        PropertyAccess,
        ThisExpression,
        SuperExpression,
    )

    registry.register(ClassDeclaration, ClassDeclarationExecutor())
    registry.register(InterfaceDeclaration, InterfaceDeclarationExecutor())
    registry.register(ContractDeclaration, ContractDeclarationExecutor())
    registry.register(NewExpression, NewExpressionExecutor())
    registry.register(PropertyAccess, PropertyAccessExecutor())
    registry.register(ThisExpression, ThisExecutor())
    registry.register(SuperExpression, SuperExecutor())
