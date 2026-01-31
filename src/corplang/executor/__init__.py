"""Settings from executor"""
from typing import Any, Optional

from src.corplang.compiler import Lexer
from src.corplang.compiler.parser import Parser
from src.corplang.executor.interpreter import Interpreter, CURRENT_INTERPRETER
from src.corplang.executor.node import NodeExecutor


def execute(entrypoint: Any, context: Optional[Any] = None) -> Optional[NodeExecutor]:
    """Execute for all nodes. Context is optional."""
    from src.corplang.executor.context import ExecutionContext, Environment
    from src.corplang.compiler.nodes import Program

    # Ensure a current Interpreter exists
    current = CURRENT_INTERPRETER.get()
    if current is None:
        from src.corplang.executor.interpreter import Interpreter
        current = Interpreter()
        # Ensure the interpreter has expected runtime attributes for compatibility with node executors
        current.current_file = None
        current.global_env = None
        current.root_context = None
        current.driver_registry = {}  # optional registry for drivers

    # Auto-register executors from /executor/nodes/*
    def _register_node_executors():
        from src.corplang.executor.nodes import statements, expressions, functions, control_flow, oop
        modules = [statements, expressions, functions, control_flow, oop]
        for mod in modules:
            # Prefer explicit register(registry) functions in modules to avoid ambiguous name-based registration
            register_fn = getattr(mod, "register", None)
            if callable(register_fn):
                # Call register; swallow duplicate-registration errors to make repeated execute() idempotent
                try:
                    register_fn(current.registry)
                except ValueError:
                    # already registered; ignore to allow multiple execute() calls in same process
                    pass
                continue

            # Fallback: scan and register concrete NodeExecutor subclasses (legacy)
            for name in dir(mod):
                obj = getattr(mod, name)
                if isinstance(obj, type):
                    try:
                        from src.corplang.executor.node import NodeExecutor

                        if not issubclass(obj, NodeExecutor):
                            continue
                    except Exception:
                        continue
                    if getattr(obj, "__abstractmethods__", None):
                        continue
                    # Infer node type name and let registry resolve to the exact AST class
                    node_type = name.replace("Executor", "")
                    if node_type:
                        try:
                            current.register(node_type, obj())
                        except Exception:
                            # Fail fast or skip non-instantiable classes
                            continue

    _register_node_executors()

    if not entrypoint:
        return None

    if context is None:
        # Ensure builtins initialized first
        current._ensure_builtins()
        # global_env always exists after setup
        # Determine a source file for this entrypoint using several possible attribute names
        entry_file = (
                getattr(entrypoint, "file", None)
                or getattr(entrypoint, "source_file", None)
                or getattr(entrypoint, "file_path", None)
                or getattr(entrypoint, "filename", None)
                or getattr(entrypoint, "path", None)
        )
        ctx = ExecutionContext(
            interpreter=current,
            environment=current.global_env,
            memory_manager=None,
            security_manager=None,
            pattern_matcher=None,
            current_file=entry_file,
        )
        # ensure interpreter runtime attrs are bound for downstream code
        try:
            current.global_env = ctx.environment
            # Initialize builtins (idempotent)
            try:
                from src.corplang.executor import builtins

                builtins.setup_builtins(current)
            except Exception:
                pass
            current.root_context = ctx
            # store current_file on interpreter for push_frame fallbacks
            current.current_file = entry_file
        except Exception:
            pass
    else:
        ctx = context

    if isinstance(entrypoint, (list, tuple)):
        result = None
        for node in entrypoint:
            result = execute(node, ctx)
        return result

    executor = current.registry.get_executor(entrypoint)
    return executor.execute(entrypoint, ctx)


def parse_file(path: str, verbose: bool = False):
    """Parse a .mp file and return the AST root node."""
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize(), path)
    if verbose:
        print(parser.as_view())
    return parser.parse()


__all__ = ["execute", "Interpreter", "parse_file"]