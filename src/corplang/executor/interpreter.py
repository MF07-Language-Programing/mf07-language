"""Minimal, self-contained Interpreter

This file implements a tiny interpreter core that does not depend on the
rest of the project. It's purposefully small: it provides a registry of
node executors and a minimal execution context so callers can register
executors and run nodes without pulling in heavy project modules.

Design goals:
- No imports from other project packages
- Simple API: `Interpreter`, `ExecutionContext`, `NodeExecutor`, `ExecutorRegistry`
- Safe default behavior for lists and None nodes
"""
import contextvars
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.corplang.executor.context import ExecutionContext, Environment
from src.corplang.executor.node import NodeExecutor

# Context var to store the current interpreter (handy for executors)
CURRENT_INTERPRETER: contextvars.ContextVar[Optional["Interpreter"]] = contextvars.ContextVar(
    "current_interpreter", default=None
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _find_installed_stdlib() -> Optional[Path]:
    """Find stdlib in installed package using sys.prefix."""
    import sys

    candidates = [
        Path(sys.prefix) / "src" / "corplang" / "stdlib",
        Path(sys.prefix) / "lib" / "python3.10" / "site-packages" / "src" / "corplang" / "stdlib",
        Path(sys.prefix) / "lib" / "python3.11" / "site-packages" / "src" / "corplang" / "stdlib",
        Path(sys.prefix) / "lib" / "python3.12" / "site-packages" / "src" / "corplang" / "stdlib",
        Path(__file__).resolve().parent.parent / "stdlib",
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    return None


def _stdlib_roots() -> list[Path]:
    roots: list[Path] = []

    custom = os.environ.get("CORPLANG_STDLIB_PATH")
    if custom:
        roots.append(Path(custom))

    active = os.environ.get("CORPLANG_ACTIVE_VERSION")
    if active and active != "local":
        roots.append(Path.home() / ".corplang" / "versions" / active / "src" / "corplang" / "stdlib")

    installed = _find_installed_stdlib()
    if installed:
        roots.append(installed)

    roots.append(_repo_root() / "src" / "corplang" / "stdlib")

    seen: set[str] = set()
    valid: list[Path] = []
    for root in roots:
        try:
            resolved = root.resolve()
        except Exception:
            continue
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        if resolved.exists():
            valid.append(resolved)
    return valid


def _normalize_module_name(module_name: str) -> str:
    name = str(module_name or "").strip()
    if name.startswith("mf."):
        name = name[3:]

    if name.startswith("core.collection.") or name == "core.collection":
        name = name.replace("core.collection", "core.collections", 1)

    return name


@lru_cache(maxsize=1)
def _load_stdlib_manifest() -> tuple[Optional[Path], dict[str, Dict[str, object]]]:
    fallback_root: Optional[Path] = None
    for root in _stdlib_roots():
        if fallback_root is None:
            fallback_root = root / "core"
        manifest_path = root / "core" / "manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            modules = data.get("modules") if isinstance(data, dict) else data
        except Exception:
            continue

        specs: dict[str, Dict[str, object]] = {}
        if isinstance(modules, list):
            for entry in modules:
                if isinstance(entry, str):
                    name = entry.strip()
                    if not name:
                        continue
                    mod_rel = name.replace("core.", "", 1) if name.startswith("core.") else name
                    specs[name] = {
                        "path": (root / "core" / f"{mod_rel.replace('.', '/')}.mp"),
                        "restricted": False,
                    }
                elif isinstance(entry, dict):
                    name = str(entry.get("name") or entry.get("module") or "").strip()
                    if not name:
                        continue
                    rel_path = entry.get("path") or entry.get("file")
                    if rel_path:
                        path = root / "core" / rel_path
                    else:
                        mod_rel = name.replace("core.", "", 1) if name.startswith("core.") else name
                        path = root / "core" / f"{mod_rel.replace('.', '/')}.mp"
                    specs[name] = {
                        "path": path,
                        "restricted": str(entry.get("security") or entry.get("policy") or "").lower() == "restricted",
                    }
        return root / "core", specs

    if fallback_root:
        return fallback_root, {}
    return None, {}


def _candidate_paths(module_name: str, current_file: Optional[str], manifest_root: Optional[Path], specs: dict[str, Dict[str, object]]) -> list[Path]:
    mod_path = module_name.replace(".", "/") + ".mp"
    candidates: list[Path] = []

    if module_name in specs:
        path = specs[module_name].get("path")
        if isinstance(path, Path):
            candidates.append(path)
        elif path:
            candidates.append(Path(path))
    elif manifest_root and module_name.startswith("core."):
        candidates.append(manifest_root / mod_path)

    if current_file:
        candidates.append(Path(current_file).parent / mod_path)

    cwd = Path.cwd()
    candidates.extend([
        cwd / mod_path,
        cwd / "src" / mod_path,
        _repo_root() / "src" / mod_path,
        _repo_root() / "examples" / mod_path,
    ])

    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


class ExecutorRegistry:
    """Registry mapping AST node classes (exact types) to a single executor.

    Rules:
    - Keys are exact classes (not loose string names).
    - Registering twice for the same node class raises an error (no silent overwrite).
    - Resolving an executor walks the node's MRO and returns the first matching registered executor.
    - If no executor is found, a LookupError is raised (fail fast).
    """

    def __init__(self):
        # Map node class -> (priority, executor)
        self._executors: Dict[type, Tuple[int, NodeExecutor]] = {}

    def _resolve_node_class(self, node_type: Any) -> type:
        """Resolve provided node_type to a class object.

        Accepts a class object or a string name (legacy). If a string is given,
        attempt to import the corresponding class from the compiler nodes module.
        """
        if isinstance(node_type, type):
            return node_type
        if isinstance(node_type, str):
            try:
                from src.corplang.compiler import nodes as _nodes

                cls = getattr(_nodes, node_type)
                if isinstance(cls, type):
                    return cls
            except Exception:
                pass
        raise TypeError(f"Unsupported node_type for registry: {node_type!r}")

    def register(self, node_type: Any, executor: NodeExecutor, priority: int = 0) -> None:
        cls = self._resolve_node_class(node_type)
        if cls in self._executors:
            raise ValueError(f"Executor already registered for node class {cls.__name__}")
        executor.priority = priority
        self._executors[cls] = (priority, executor)

    def get_executor(self, node: Any) -> NodeExecutor:
        """Return the executor for the given node, checking the node's MRO.

        Raises LookupError if no executor is found for any class in the MRO.
        """
        if node is None:
            raise ValueError("Cannot execute None node")
        mro = type(node).__mro__
        for cls in mro:
            if cls in self._executors:
                _, executor = self._executors[cls]
                # allow executor to validate node if needed
                try:
                    if executor.can_execute(node):
                        return executor
                    # if can_execute returns False, keep searching
                except Exception:
                    # failing can_execute should not hide the fact a registration exists
                    raise
        # No executor found
        raise LookupError(f"No executor registered for node type {type(node).__name__}")


def register_executor(registry: ExecutorRegistry, *node_types: Any, priority: int = 0):
    """Decorator helper to register an executor class instance with the registry."""

    def decorator(executor_cls):
        instance = executor_cls()
        for ntype in node_types:
            registry.register(ntype, instance, priority=priority)
        return executor_cls

    return decorator


class Interpreter:
    """Minimal interpreter that resolves executors from a single ExecutorRegistry

    The Interpreter is responsible for:
    - creating a single ExecutionContext for an invocation when none is provided
    - resolving the executor for each node at execution time via the registry
    - propagating the same context across recursive calls
    """

    def __init__(self) -> None:
        self.registry = ExecutorRegistry()
        self._token = CURRENT_INTERPRETER.set(self)
        # runtime defaults expected by executors
        from src.corplang.core.exceptions import CorpLangRuntimeError

        self.error_class = CorpLangRuntimeError
        self.current_file = None
        self.global_env = None
        self.root_context = None
        self.driver_registry = {}
        # Execution flags/defaults
        self.strict_types = False
        self.runtime_source_root = None
        self.current_module_path = None
        # Module cache for imports
        self._module_cache = {}
        # Track modules currently being imported to break recursive imports
        self._module_loading: set[str] = set()
        # Lazy flag for executor registrations
        self._executors_initialized: bool = False
        # Call stack: list of frames (language-level stack), most recent last
        self.call_stack: list = []
        # When True, diagnostics may include internal host traces — default False in production
        self.show_internal_diagnostics: bool = False
        self._builtins_initialized = False

    def _snapshot_call_stack(self) -> list[dict]:
        """Return a sanitized, shallow copy of the current language call stack.

        Locals are omitted from the payload to avoid leaking heavy host objects into
        language-level exceptions while keeping file/line/function metadata intact.
        """
        snapshot: list[dict] = []
        for frame in list(self.call_stack or []):
            if not isinstance(frame, dict):
                continue
            try:
                snapshot.append(
                    {
                        "file": frame.get("origin_file") or frame.get("file") or frame.get("filename") or frame.get("path"),
                        "line": frame.get("line"),
                        "origin_line": frame.get("origin_line"),
                        "column": frame.get("column"),
                        "function": frame.get("function") or frame.get("name") or frame.get("fn"),
                    }
                )
            except Exception:
                continue
        return snapshot

    def _attach_stacktrace_to_payload(self, payload: Any, frames: list[dict]) -> None:
        """Attach language stack trace frames to a language-level payload if possible."""
        if payload is None:
            return
        try:
            from src.corplang.executor.objects import InstanceObject

            if isinstance(payload, InstanceObject):
                try:
                    payload.set("stacktrace", frames)
                    return
                except Exception:
                    pass
        except Exception:
            pass

        # Fallbacks: attribute or mapping assignment
        try:
            if hasattr(payload, "stacktrace"):
                setattr(payload, "stacktrace", frames)
                return
        except Exception:
            pass

        try:
            if isinstance(payload, dict):
                payload["stacktrace"] = frames
        except Exception:
            pass

    def _ensure_builtins(self):
        """Ensure builtins are initialized before importing stdlib modules."""
        if self._builtins_initialized:
            return
        
        if self.global_env is None:
            from src.corplang.executor.context import Environment
            self.global_env = Environment()
            # Initialize a minimal root context for constructor calls
            try:
                from src.corplang.executor.context import ExecutionContext

                self.root_context = ExecutionContext(
                    interpreter=self,
                    environment=self.global_env,
                    memory_manager=None,
                    security_manager=None,
                    pattern_matcher=None,
                )
            except Exception:
                self.root_context = None
        
        try:
            from src.corplang.executor import builtins
            builtins.setup_builtins(self)
            self._builtins_initialized = True
        except Exception:
            pass

    def _ensure_node_executors(self):
        """Register builtin node executors once for this interpreter."""
        if self._executors_initialized:
            return

        try:
            from src.corplang.executor.nodes import control_flow, expressions, functions, oop, statements

            modules = [statements, expressions, functions, control_flow, oop]
            for mod in modules:
                register_fn = getattr(mod, "register", None)
                if callable(register_fn):
                    try:
                        register_fn(self.registry)
                    except ValueError:
                        # Duplicate registration is safe to ignore
                        pass
            self._executors_initialized = True
        except Exception:
            # Leave flag as False so a later attempt can retry
            self._executors_initialized = False

    def _import_module(self, module_name: str, current_file: str = None):
        """Module importer that understands stdlib manifest and active version paths."""
        normalized = _normalize_module_name(module_name)

        if normalized in self._module_cache:
            return self._module_cache[normalized]

        if normalized in self._module_loading:
            # Re-entrant import; return any partial cache to avoid infinite recursion
            return self._module_cache.get(normalized, {})

        self._module_loading.add(normalized)
        # Seed cache early to break recursive imports during module execution
        self._module_cache.setdefault(normalized, {})

        # Initialize builtins after seeding recursion guards to avoid re-entrant loops
        self._ensure_builtins()

        manifest_root, specs = _load_stdlib_manifest()

        spec = specs.get(normalized)
        if spec and spec.get("restricted"):
            from src.corplang.core.exceptions import CorpLangRuntimeError, RuntimeErrorType

            raise CorpLangRuntimeError(
                f"Module '{normalized}' is restricted by stdlib policy",
                RuntimeErrorType.SECURITY_ERROR,
                file_name=current_file,
            )

        candidates = _candidate_paths(normalized, current_file, manifest_root, specs)
        found: Optional[Path] = None
        for candidate in candidates:
            if candidate.is_file():
                found = candidate
                break

        if not found:
            prefix = f"{normalized}."
            package_members = [name for name in specs if name.startswith(prefix)] if specs else []
            if package_members:
                exports: Dict[str, Any] = {}
                for name in sorted(package_members):
                    meta = specs.get(name) or {}
                    if meta.get("restricted"):
                        continue
                    exports.update(self._import_module(name, current_file))
                self._module_cache[normalized] = exports
                self._module_loading.discard(normalized)
                return exports

            self._module_cache[normalized] = {}
            self._module_loading.discard(normalized)
            return {}

        from src.corplang.executor import parse_file
        from src.corplang.executor.context import Environment, ExecutionContext

        ast = parse_file(str(found))
        # Module environment has global_env (builtins) as parent
        # This ensures module-level code can access builtins
        # and class_ref._env will have proper scope chain
        env = Environment(parent=self.global_env)
        ctx = ExecutionContext(
            interpreter=self,
            environment=env,
            memory_manager=None,
            security_manager=None,
            pattern_matcher=None,
            current_file=str(found),
        )
        self.current_file = str(found)
        try:
            self._ensure_node_executors()
            self.execute(ast, ctx)
            exports = dict(env.variables)
        except Exception as exec_err:
            exports = {}
        finally:
            self._module_loading.discard(normalized)

        self._module_cache[normalized] = exports
        return exports

    def register(self, node_type: Any, executor: NodeExecutor, priority: int = 0) -> None:
        self.registry.register(node_type, executor, priority)

    def push_frame(self, file: Optional[str], line: Optional[int], function: Optional[str], locals_map: Optional[Dict[str, Any]] = None, column: Optional[int] = None, node: Optional[Any] = None, origin_file: Optional[str] = None, origin_line: Optional[int] = None):
        """Push a language-level frame onto the interpreter call stack."""
        # Store both the declared line and the node-origin line to allow later
        # diagnostics to prefer the most precise execution location.
        resolved_file = (
            file
            or origin_file
            or getattr(node, "file", None)
            or getattr(node, "file_path", None)
            or getattr(node, "source_file", None)
            or self.current_file
        )
        declared_line = line or getattr(node, "line", None)
        origin_line_final = origin_line
        frame = {
            "file": resolved_file,
            "line": declared_line,
            "origin_line": origin_line_final,
            "column": column or getattr(node, "column", None),
            "function": function or "<unknown>",
            "node": type(node).__name__ if node is not None else None,
            "locals": dict(locals_map or {}),
        }
        self.call_stack.append(frame)

    def pop_frame(self):
        """Pop the last frame from the call stack."""
        try:
            return self.call_stack.pop()
        except Exception:
            return None

    def execute(self, node: Any, context: Optional[ExecutionContext] = None) -> Any:
        """Execute node(s) using the registry to resolve executors.

        If `context` is None, create a single `ExecutionContext` and reuse it
        for the duration of this top-level call.
        """

        # Lazy import of richer ExecutionContext when we need to construct a default
        if context is None:
            ctx = ExecutionContext(
                interpreter=self,
                environment=Environment(),
                memory_manager=None,
                security_manager=None,
                pattern_matcher=None,
            )
        else:
            ctx = context

        if node is None:
            return None

        if isinstance(node, (list, tuple)):
            result = None
            for n in node:
                result = self.execute(n, ctx)
            return result

        # Resolve executor at the point of execution
        executor = self.registry.get_executor(node)

        # Push a transient frame for the exact AST node being executed to increase precision
        pushed_node_frame = False
        try:
            try:
                node_file = (
                    getattr(node, "file", None)
                    or getattr(node, "file_path", None)
                    or getattr(node, "source_file", None)
                    or self.current_file
                )
                node_line = getattr(node, "line", None)
                # For Identifiers, use the node type, not the name (which is the variable being accessed)
                node_type = type(node).__name__
                node_fn = None
                if node_type not in ("Identifier", "GenericIdentifier", "Literal", "BinaryOp", "UnaryOp", "IndexAccess"):
                    node_fn = getattr(node, "name", None)
                if not node_fn:
                    node_fn = node_type
                locals_map = getattr(ctx, "environment", None).variables if getattr(ctx, "environment", None) is not None else None
                self.push_frame(node_file, node_line, node_fn, locals_map=locals_map, node=node)
                pushed_node_frame = True
            except Exception:
                pushed_node_frame = False

            return executor.execute(node, ctx)
        except Exception as exc:
            # Ensure we attach a language-level call stack snapshot to the error
            stack_snapshot = self._snapshot_call_stack()
            try:
                # If this is already a CorpLangRuntimeError, enrich and re-raise
                from src.corplang.core.exceptions import (
                    CorpLangRuntimeError,
                    InternalRuntimeError,
                    CorpLangRaisedException,
                    ReturnException,
                    RuntimeErrorType,
                    BreakException,
                    ContinueException,
                )

                # BreakException and ContinueException are control-flow signals
                # that must propagate unmodified to their enclosing loops
                if isinstance(exc, (BreakException, ContinueException)):
                    raise

                # If a ReturnException escaped to the interpreter layer, we should only
                # convert it to a language error when there is no enclosing function-like
                # frame that can (and should) handle it. If such a frame exists, allow the
                # ReturnException to propagate so callers like bind_and_exec can catch it.
                if isinstance(exc, ReturnException):
                    # If the current execution context is a top-level context (no parent), a
                    # ReturnException is stray and should be reported as a syntax/runtime
                    # error. If we're inside a nested context (child spawned by a call), let
                    # the ReturnException propagate to the caller (e.g., bind_and_exec).
                    try:
                        is_top_level_ctx = (ctx is not None and getattr(ctx, "parent_context", None) is None)
                    except Exception:
                        is_top_level_ctx = True

                    if not is_top_level_ctx:
                        # Let callers handle ReturnException (normal flow for functions/methods)
                        raise

                    try:
                        err = CorpLangRuntimeError(
                            "Return statement outside of function",
                            RuntimeErrorType.SYNTAX_ERROR,
                            node=node,
                        )
                        err.mp_stack = stack_snapshot
                        err.interpreter = self
                    except Exception:
                        err = CorpLangRuntimeError("Return statement outside of function", RuntimeErrorType.SYNTAX_ERROR)
                    raise err

                if isinstance(exc, CorpLangRaisedException):
                    try:
                        frames = getattr(exc, "mp_stack", None)
                        if not frames:
                            frames = stack_snapshot
                            exc.mp_stack = frames
                        self._attach_stacktrace_to_payload(getattr(exc, "value", None), frames)
                    except Exception:
                        pass
                    # Propagate language-level exceptions unchanged so TryExecutor can match typed catches
                    raise

                if isinstance(exc, CorpLangRuntimeError):
                    try:
                        if getattr(exc, "mp_stack", None) in (None, []):
                            exc.mp_stack = stack_snapshot
                    except Exception:
                        pass
                    # allow consumer to call printStackTrace()
                    try:
                        exc.interpreter = self
                    except Exception:
                        pass
                    raise

                # Wrap unknown host exception as InternalRuntimeError (host traces hidden by default)
                # Keep the original exception as 'cause'
                try:
                    from src.corplang.tools.diagnostics import safe_message
                    wrapped = InternalRuntimeError(safe_message(exc), cause=exc)
                    wrapped.mp_stack = stack_snapshot
                    wrapped.interpreter = self
                except Exception:
                    # Fallback: create generic CorpLangRuntimeError with safe message
                    try:
                        from src.corplang.tools.diagnostics import safe_message
                        msg = safe_message(exc)
                    except Exception:
                        msg = "<unrepresentable exception>"
                    wrapped = CorpLangRuntimeError(msg, RuntimeErrorType.RUNTIME_ERROR)
                    wrapped.mp_stack = stack_snapshot
                    try:
                        wrapped.interpreter = self
                    except Exception:
                        pass
                raise wrapped
            except Exception:
                # If enrichment fails, re-raise original to avoid masking
                raise
        finally:
            if pushed_node_frame:
                try:
                    self.pop_frame()
                except Exception:
                    pass

    def interpret(self, program: Any, context: Optional[ExecutionContext] = None) -> Any:
        """Convenience wrapper that temporarily sets this interpreter as current."""
        token = CURRENT_INTERPRETER.set(self)
        try:
            return self.execute(program, context)
        finally:
            CURRENT_INTERPRETER.reset(token)


__all__ = ["Interpreter", "ExecutionContext", "NodeExecutor", "ExecutorRegistry", "CURRENT_INTERPRETER",
           "register_executor"]
