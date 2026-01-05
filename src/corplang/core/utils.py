"""Utility functions for corp lang runtime."""
from typing import List, Any, Optional, Dict, TYPE_CHECKING

from src.corplang.compiler.nodes import ASTNode
from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType, ReturnException
from src.corplang.executor.context import Environment

if TYPE_CHECKING:
    from src.corplang.executor.interpreter import Interpreter


# noinspection PyBroadException
def evaluate_default_value(default_node: Any, interpreter: "Interpreter") -> Any:
    if default_node is None:
        return None
    try:
        if not isinstance(default_node, ASTNode):
            return default_node
    except Exception:
        pass
    try:
        return interpreter.execute(default_node, interpreter.root_context)
    except Exception:
        return None


def safe_attr(obj, *names):
    for n in names:
        val = getattr(obj, n, None)
        if val is not None:
            return val
    return None


def bind_and_exec(interpreter, decl, closure_env, args, kwargs, ctx, this=None, class_ref=None):
    """Execute function/method body with arguments bound to closure environment.
    
    Args:
        interpreter: Interpreter instance
        decl: Function/method AST node
        closure_env: Closure environment (parent scope where function was defined)
        args: Positional arguments
        kwargs: Keyword arguments
        ctx: Current execution context
        this: Instance reference for methods
        class_ref: Class reference for methods
        
    The execution environment hierarchy:
        method_locals (params, this, class_ref) → closure_env → module_env → builtins
    """
    params = getattr(decl, "params", []) or []
    defaults = getattr(decl, "param_defaults", {}) or {}
    bound = bind_arguments_to_params(
        params, defaults, list(args), dict(kwargs or {}), interpreter, decl
    )

    # Add special bindings to locals
    if this is not None:
        bound["this"] = this
    if class_ref is not None:
        bound[class_ref.name] = class_ref

    # Create method environment with closure as parent
    # This ensures method can access variables from module where it was defined
    method_env = Environment(closure_env)
    for k, v in bound.items():
        method_env.define(k, v)
    
    # Create child context with method environment
    child = ctx.spawn(method_env)
    
    # Set file context from declaration, not from mutable interpreter.current_file
    decl_file = safe_attr(decl, "file", "source_file", "filename")
    if decl_file:
        child.current_file = decl_file
    
    # Mark as async if needed
    child.is_async = bool(getattr(decl, "is_async", False))
    
    # Enter class scope for access control if applicable
    if class_ref is not None and hasattr(child, "push_scope"):
        try:
            child = child.push_scope(
                getattr(class_ref, "name", None) or getattr(class_ref, "__name__", None), 
                this
            )
        except Exception:
            pass

    try:
        with child.frame(
            decl_file or child.current_file,
            getattr(decl, "line", None),
            getattr(decl, "name", None),
            node=decl,
        ):
            result = None
            for stmt in getattr(decl, "body", []) or []:
                result = interpreter.execute(stmt, child)
            return result
    except ReturnException as r:
        return r.value


def bind_arguments_to_params(
    params: List[str],
    defaults: Optional[Dict[str, Any]],
    positional_args: List[Any],
    keyword_args: Optional[Dict[str, Any]],
    interpreter: "Interpreter",
    node: Optional[ASTNode] = None,
) -> Dict[str, Any]:
    def _param_name(p):
        if isinstance(p, str):
            return p
        return getattr(p, "name", None) or getattr(p, "identifier", None)

    normalized_params = []
    for p in params or []:
        pname = _param_name(p)
        if not pname:
            raise CorpLangRuntimeError(
                "Parameter is missing a name",
                RuntimeErrorType.SYNTAX_ERROR,
                node=node,
            )
        normalized_params.append(pname)

    normalized_defaults: Dict[str, Any] = {}
    for key, val in (defaults or {}).items():
        pname = _param_name(key)
        if pname:
            normalized_defaults[pname] = val

    bound: Dict[str, Any] = {}
    defaults = normalized_defaults
    remaining_kwargs = dict(keyword_args or {})

    if len(positional_args) > len(normalized_params):
        raise CorpLangRuntimeError(
            f"Too many positional arguments: expected {len(normalized_params)}, got {len(positional_args)}",
            RuntimeErrorType.TYPE_ERROR,
            node=node,
            suggestions=["Remove extra positional arguments or convert them to named arguments"],
        )

    # Support a trailing 'kwargs' parameter to capture extra named args.
    kw_catcher = None
    if normalized_params:
        last = normalized_params[-1]
        if isinstance(last, str) and last == "kwargs":
            kw_catcher = last
            normalized_params = normalized_params[:-1]

    for idx, pname in enumerate(normalized_params):
        if idx < len(positional_args):
            if pname in remaining_kwargs:
                raise CorpLangRuntimeError(
                    f"Argument '{pname}' specified by position and by name",
                    RuntimeErrorType.TYPE_ERROR,
                    node=node,
                    suggestions=["Pass each argument only once"],
                )
            bound[pname] = positional_args[idx]
            continue

        if pname in remaining_kwargs:
            bound[pname] = remaining_kwargs.pop(pname)
            continue

        if pname in defaults and defaults[pname] is not None:
            bound[pname] = evaluate_default_value(defaults[pname], interpreter)
            continue

        raise CorpLangRuntimeError(
            f"Missing required argument '{pname}'",
            RuntimeErrorType.TYPE_ERROR,
            node=node,
            suggestions=[
                "Provide the argument positionally or by name",
                "Add a default value if optional",
            ],
        )

    # If we have a kwargs catcher, bind remaining kwargs into it (even if empty)
    if kw_catcher is not None:
        # If caller explicitly provided a value for 'kwargs', prefer that
        if kw_catcher in remaining_kwargs:
            bound[kw_catcher] = remaining_kwargs.pop(kw_catcher)
        else:
            bound[kw_catcher] = dict(remaining_kwargs or {})
        remaining_kwargs = {}

    if remaining_kwargs:
        unexpected = ", ".join(sorted(remaining_kwargs.keys()))
        raise CorpLangRuntimeError(
            f"Unexpected argument(s): {unexpected}",
            RuntimeErrorType.TYPE_ERROR,
            node=node,
            suggestions=["Remove unsupported named arguments", "Check parameter names for typos"],
        )

    return bound
