"""Built-in helpers and environment setup for the interpreter.
"""
import base64
import hashlib
import json
import time
from typing import Any, Dict

from src.corplang.executor.objects import InstanceObject
from src.corplang.executor import helpers as core_helpers
from src.corplang.core.exceptions import RuntimeErrorType
from src.corplang.executor.type_system import type_from_annotation, type_from_value, TypeObject


def setup_builtins(interpreter) -> None:
    """Populate `interpreter.global_env` with builtin names and attach
    a small set of helper callables onto the interpreter for backwards
    compatibility.
    """

    def _builtin_print(*args):
        print(*args)
        return None

    def _builtin_type(obj):
        try:
            return core_helpers.literal_type_name(obj)
        except Exception as e:
            return f"unknown_type_error({e})"

    def _builtin_typeOf(obj):
        try:
            return type_from_value(obj, interpreter)
        except Exception:
            return type_from_value(None, interpreter)

    def _builtin_len(obj):
        try:
            if isinstance(obj, str):
                return len(obj)
            if hasattr(obj, "__len__"):
                return len(obj)
            if isinstance(obj, InstanceObject):
                try:
                    size_fn = obj.get("size")
                    if callable(size_fn):
                        return size_fn()
                except Exception:
                    pass
                try:
                    raw_fn = obj.get("__raw__")
                    if callable(raw_fn):
                        raw = raw_fn()
                        if isinstance(raw, (list, tuple, dict, set, str, bytes)):
                            return len(raw)
                except Exception:
                    pass
            size_attr = getattr(obj, "size", None)
            if callable(size_attr):
                return size_attr()
            length_attr = getattr(obj, "length", None)
            if callable(length_attr):
                return length_attr()
            raw_attr = getattr(obj, "__raw__", None)
            if callable(raw_attr):
                raw = raw_attr()
                if isinstance(raw, (list, tuple, dict, set, str, bytes)):
                    return len(raw)
        except Exception:
            pass
        raise interpreter.error_class(
            f"Object of type {core_helpers.literal_type_name(obj)} has no len()",
            RuntimeErrorType.TYPE_ERROR,
        )

    def _builtin_range(*args):
        return list(range(*args))

    def _builtin_wait_seconds(seconds):
        time.sleep(seconds)
        return None

    def _builtin_str(obj=None):
        """Convert value to string in a forgiving way."""
        try:
            return "" if obj is None else str(obj)
        except Exception:
            return f"<str-error {type(obj).__name__}>"

    def _builtin_genericOf(obj):
        """Return generic type arguments of an instance as a dict of TypeObjects."""
        if not isinstance(obj, InstanceObject):
            return {}

        generics = getattr(obj, '__generics__', None)
        if not generics:
            return {}

        result = {}
        class_obj = getattr(obj, 'class_ref', None)
        declaration = getattr(class_obj, 'declaration', None) if class_obj else None
        type_params = getattr(declaration, 'type_parameters', None) or []

        for idx, type_annotation in generics.items():
            if idx >= len(type_params):
                continue
            param_name = type_params[idx]
            try:
                result[param_name] = type_from_annotation(type_annotation, interpreter)
            except Exception:
                result[param_name] = TypeObject(getattr(type_annotation, 'base', 'any'))

        return result if result else {}

    import importlib
    import builtins

    def _builtin_native(func_path: str, *args, **kwargs):
        try:
            if "." in func_path:
                parts = func_path.split(".")
                module_path = ".".join(parts[:-1])
                attr_name = parts[-1]
                module = importlib.import_module(module_path)
                attr = getattr(module, attr_name)
                if callable(attr):
                    return attr(*args, **kwargs)
                if not args and not kwargs:
                    return attr
                raise interpreter.error_class(
                    f"__native__: '{func_path}' is not callable (got {type(attr).__name__})",
                    RuntimeErrorType.TYPE_ERROR,
                )
            if hasattr(builtins, func_path):
                func = getattr(builtins, func_path)
                return func(*args, **kwargs)
            common_modules = {
                "math": "math",
                "random": "random",
                "os": "os",
                "sys": "sys",
                "json": "json",
                "re": "re",
                "datetime": "datetime",
                "time": "time",
                "collections": "collections",
                "itertools": "itertools",
                "functools": "functools",
                "operator": "operator",
                "secrets": "secrets",
                "uuid": "uuid",
                "hashlib": "hashlib",
                "base64": "base64",
            }
            for mod_name in common_modules.values():
                try:
                    module = importlib.import_module(mod_name)
                    if hasattr(module, func_path):
                        func = getattr(module, func_path)
                        return func(*args, **kwargs)
                except Exception:
                    continue
            raise interpreter.error_class(
                f"__native__: Function '{func_path}' not found in builtins or common modules",
                RuntimeErrorType.REFERENCE_ERROR,
            )
        except interpreter.error_class:
            raise
        except Exception as e:
            # Preserve original python exception as 'cause' for better diagnostics/matching
            err = interpreter.error_class(f"__native__: Error calling '{func_path}': {e}", RuntimeErrorType.RUNTIME_ERROR)
            try:
                setattr(err, "cause", e)
                err.__cause__ = e
            except Exception:
                pass
            raise err from e

    # Simple interactive helper that reads from environment MF_INPUTS when available.
    def _builtin_input(prompt: str = None, expected_type: Any = None, **kwargs):
        """Read input from the user, optionally cast to expected_type.

        Behavior:
        - If env MF_INPUTS is set, read values separated by '|' from it in order.
        - `expected_type` may be a string like 'int', 'float', 'bool', 'int|float' or 'any', or any object whose `str()` yields a type name.
        - `raise` (bool) can be passed as named arg; when True, input/cast errors raise with full traceback. When False (default), a short error message is shown and the prompt is repeated.
        """
        import os

        # Prepare buffer on interpreter if not present
        if not hasattr(interpreter, "_input_buffer"):
            buf = os.environ.get("MF_INPUTS", "")
            interpreter._input_buffer = [s for s in buf.split("|") if s != ""] if buf else []
            interpreter._input_index = 0

        # Determine whether to raise on cast errors or to re-prompt (default: do not raise)
        raise_on_error = bool(kwargs.get("raise", False) or kwargs.get("raise_traceback", False))

        # Loop until we get a valid cast (or raise if configured)
        while True:
            # Prefer env-provided input when available (non-interactive). Do NOT print prompt in this mode to avoid duplicates.
            if getattr(interpreter, "_input_index", 0) < len(getattr(interpreter, "_input_buffer", [])):
                val = interpreter._input_buffer[interpreter._input_index]
                interpreter._input_index += 1
                interactive_read = False
            else:
                # Fall back to interactive stdin (blocking) - print prompt once then read
                try:
                    if prompt:
                        try:
                            interpreter._builtin_print(prompt)
                        except Exception:
                            pass
                    # Avoid duplicate prompt printing: we already printed via interpreter._builtin_print
                    val = input("")
                except Exception as e:
                    raise interpreter.error_class(f"input() failed: {e}", RuntimeErrorType.RUNTIME_ERROR)
                interactive_read = True

            # If no expected_type provided, return raw string
            if not expected_type:
                return val

            # Normalize expected_type to string if provided as type name
            if isinstance(expected_type, str):
                et = expected_type
            else:
                try:
                    et = str(expected_type)
                except Exception:
                    et = None

            if not et:
                return val

            # Try to cast according to type (support unions)
            # On cast error: if raise_on_error, propagate; otherwise print short message and loop to ask again.
            try:
                if "|" in et:
                    last_exc = None
                    for part in et.split("|"):
                        part = part.strip()
                        try:
                            return _do_cast(val, part, interpreter)
                        except interpreter.error_class as e:
                            last_exc = e
                            continue
                    # none matched
                    raise last_exc or interpreter.error_class(f"Cannot cast input '{val}' to any of {et}", RuntimeErrorType.TYPE_ERROR)
                else:
                    return _do_cast(val, et.strip(), interpreter)
            except interpreter.error_class as e:
                if raise_on_error:
                    # Expose full traceback to caller
                    raise
                # Otherwise, show a short message and re-prompt (or consume next buffered value)
                try:
                    interpreter._builtin_print(f"Invalid input: {str(e).splitlines()[0]}")
                except Exception:
                    pass
                # continue loop to read next value
                continue

    def _do_cast(value: str, et: str, interpreter):
        etl = et.lower()
        if etl in ("str", "string"):
            return value
        if etl in ("int", "integer"):
            try:
                return int(value)
            except Exception:
                raise interpreter.error_class(f"Cannot cast '{value}' to int", RuntimeErrorType.TYPE_ERROR)
        if etl in ("float", "double"):
            try:
                return float(value)
            except Exception:
                raise interpreter.error_class(f"Cannot cast '{value}' to float", RuntimeErrorType.TYPE_ERROR)
        if etl in ("bool", "boolean"):
            v = value.strip().lower()
            if v in ("true", "1", "yes", "y"):
                return True
            if v in ("false", "0", "no", "n"):
                return False
            raise interpreter.error_class(f"Cannot cast '{value}' to bool", RuntimeErrorType.TYPE_ERROR)
        if etl == "any":
            return value
        # Try to resolve a class name in global env
        try:
            if et in interpreter.global_env.variables:
                # If it's a class, we cannot cast a string into an instance automatically
                # so we just return the string and rely on downstream checks
                return value
        except Exception:
            pass
        raise interpreter.error_class(f"Unknown expected type '{et}' for input()", RuntimeErrorType.TYPE_ERROR)

    # Small utility namespace
    def _safe_b64_decode(s: Any) -> str:
        try:
            return base64.b64decode(str(s).encode()).decode(errors="ignore")
        except Exception:
            return ""

    mf_hash = {
        "md5": lambda s: hashlib.md5(str(s).encode()).hexdigest(),
        "sha256": lambda s: hashlib.sha256(str(s).encode()).hexdigest(),
        "base64_encode": lambda s: base64.b64encode(str(s).encode()).decode(),
        "base64_decode": _safe_b64_decode,
    }

    mf_json = {"parse": lambda s: json.loads(s) if isinstance(s, str) else None, "stringify": lambda o, indent=None: json.dumps(o, ensure_ascii=False, indent=int(indent) if indent else None)}

    import datetime as dt_module

    mf_datetime = {
        "now": lambda: dt_module.datetime.now(),
        "today": lambda: dt_module.datetime.today(),
        "from_timestamp": lambda ts: dt_module.datetime.fromtimestamp(ts),
        "fromisoformat": lambda s: dt_module.datetime.fromisoformat(s),
        "format": lambda native_dt, fmt: native_dt.strftime(fmt) if hasattr(native_dt, 'strftime') else None,
        "format_ms": lambda native_dt, fmt: native_dt.strftime(fmt) if hasattr(native_dt, 'strftime') else None,
        "to_timestamp": lambda native_dt: native_dt.timestamp() if hasattr(native_dt, 'timestamp') else None,
    }

    mf_objects = {
        "Map": lambda: {},
        "keys": lambda d: list(d.keys()) if isinstance(d, dict) else [],
        "values": lambda d: list(d.values()) if isinstance(d, dict) else [],
        "mapHas": lambda d, k: k in d if isinstance(d, dict) else False,
        "mapGet": lambda d, k, default=None: d.get(k, default) if isinstance(d, dict) else default,
        "mapPut": lambda d, k, v: d.__setitem__(k, v) if isinstance(d, dict) else None,
        "mapRemove": lambda d, k: d.pop(k, None) if isinstance(d, dict) else None,
    }

    mf_namespace: Dict[str, Any] = {
        "json": mf_json,
        "hash": mf_hash,
        "datetime": mf_datetime,
        "objects": mf_objects,
        "utils": {},
        "random": {},
        "http": None,
    }

    # Attach convenience functions to interpreter for compatibility
    interpreter._builtin_print = _builtin_print
    interpreter._builtin_type = _builtin_type
    interpreter._builtin_len = _builtin_len
    interpreter._builtin_range = _builtin_range
    interpreter._builtin_wait_seconds = _builtin_wait_seconds
    interpreter._builtin_str = _builtin_str
    interpreter._builtin_native = _builtin_native
    interpreter._builtin_genericOf = _builtin_genericOf
    interpreter._builtin_typeOf = _builtin_typeOf

    # Register basic names in global environment
    ge = interpreter.global_env
    ge.define("print", _builtin_print, "function")
    ge.define("sout", _builtin_print, "function")
    ge.define("type", _builtin_type, "function")
    ge.define("typeOf", _builtin_typeOf, "function")
    ge.define("len", _builtin_len, "function")
    ge.define("range", _builtin_range, "function")
    ge.define("waitSeconds", _builtin_wait_seconds, "function")
    ge.define("str", _builtin_str, "function")
    ge.define("__native__", _builtin_native, "function")
    ge.define("genericOf", _builtin_genericOf, "function")

    # minimal mf namespace exposure
    ge.define("mf", mf_namespace, "object")
    ge.define("mf.json", mf_json, "object")
    ge.define("mf.hash", mf_hash, "module")
    ge.define("mf.datetime", mf_datetime, "module")
    ge.define("mf.objects", mf_objects, "module")

    # Ensure native exception classes are globally visible for typed catch/throw
    try:
        exports = interpreter._import_module("core.lang.exceptions")
        if isinstance(exports, dict):
            for name, val in exports.items():
                if name in ("Exception", "Error", "RuntimeError", "TypeError", "GenericContractError", "RuntimeException"):
                    try:
                        ge.define(name, val, "class")
                    except Exception:
                        ge.variables[name] = val
    except Exception:
        pass

    # input() helper for interactive/non-interactive demos
    ge.define("input", _builtin_input, "function")
    # testing helper: raise a named Python exception (for demos/tests)
    def _builtin_raise(exc_name: str, *args):
        """Raise a Python exception by name for demonstration purposes.

        Supported names: FileNotFoundError, IOError, TimeoutError, ValueError, AssertionError
        """
        import asyncio
        name = (exc_name or "").strip()
        if name == "FileNotFoundError":
            raise FileNotFoundError(*args)
        if name in ("IOError", "OSError"):
            raise OSError(*args)
        if name == "TimeoutError":
            # Map to asyncio.TimeoutError if available
            try:
                raise asyncio.TimeoutError(*args)
            except Exception:
                raise TimeoutError(*args)
        if name == "ValueError":
            raise ValueError(*args)
        if name == "AssertionError":
            raise AssertionError(*args)
        # Fallback: generic RuntimeError
        raise RuntimeError(*args)

    ge.define("raise_error", _builtin_raise, "function")