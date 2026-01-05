from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.corplang.executor.interpreter import Interpreter

from src.corplang.executor import helpers as core_helpers
from src.corplang.executor.helpers import frame


class Environment:
    """Lexical scope with parent chaining and optional type metadata."""

    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.types: Dict[str, Any] = {}

    def define(self, name: str, value: Any, type_annotation: Optional[str] = None):
        """Define a variable in the current scope."""
        self.variables[name] = value
        if type_annotation:
            self.types[name] = type_annotation

    def get(self, name: str) -> Any:
        """Retrieve a variable value, walking up the scope chain."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise KeyError(name)

    def set(self, name: str, value: Any):
        """Update an existing variable in the scope chain."""
        if name in self.variables:
            self.variables[name] = value
            return
        if self.parent:
            self.parent.set(name, value)
            return
        raise KeyError(name)

    def has(self, name: str) -> bool:
        """Check if a variable exists in the scope chain."""
        if name in self.variables:
            return True
        return self.parent.has(name) if self.parent else False


@dataclass
class ExecutionContext:
    """Runtime execution context with scope, security, and diagnostics."""

    interpreter: "Interpreter"
    environment: Environment
    memory_manager: Any
    security_manager: Any
    pattern_matcher: Any

    parent_context: Optional["ExecutionContext"] = None
    current_file: Optional[str] = None

    # Whether the current context is asynchronous (inside an async intent/function)
    is_async: bool = False

    # Access control
    current_scope_owner: Optional[str] = None
    current_instance: Optional[Any] = None

    # Observability hook
    observability_callback: Optional[callable] = None

    def child(self, locals_map: Optional[Dict[str, Any]] = None) -> "ExecutionContext":
        """Create a child context with a new lexical environment."""

        env = Environment(self.environment)

        if locals_map:
            for k, v in locals_map.items():
                env.define(k, v)

        return ExecutionContext(
            interpreter=self.interpreter,
            environment=env,
            memory_manager=self.memory_manager,
            security_manager=self.security_manager,
            pattern_matcher=self.pattern_matcher,
            parent_context=self,
            current_file=self.current_file,
            current_scope_owner=self.current_scope_owner,
            current_instance=self.current_instance,
        )

    def spawn(self, env: Environment, current_file: Optional[str] = None) -> "ExecutionContext":
        """Spawn a context using an existing environment."""
        return ExecutionContext(
            interpreter=self.interpreter,
            environment=env,
            memory_manager=self.memory_manager,
            security_manager=self.security_manager,
            pattern_matcher=self.pattern_matcher,
            parent_context=self,
            current_file=current_file or self.current_file,
            current_scope_owner=self.current_scope_owner,
            current_instance=self.current_instance,
        )

    def define_var(self, name: str, value: Any, type_annotation: Optional[str] = None):
        """Define a variable in the current environment."""
        self.environment.define(name, value, type_annotation)

    def get_var(self, name: str) -> Any:
        """Get a variable or raise a runtime error."""
        try:
            return self.environment.get(name)
        except KeyError:
            raise self.interpreter.error_class(f"Undefined variable: {name}")

    def set_var(self, name: str, value: Any):
        """Set a variable value with optional type checking."""
        if self.interpreter.strict_types:
            expected = None
            env = self.environment
            while env and expected is None:
                expected = env.types.get(name)
                env = env.parent

            if expected and not core_helpers.matches_type(value, expected):
                # noinspection PyProtectedMember
                raise self.interpreter.error_class(
                    f"Type mismatch for variable '{name}': "
                    f"expected {expected}, got {core_helpers.literal_type_name(value)}"
                )

        try:
            self.environment.set(name, value)
        except KeyError:
            raise self.interpreter.error_class(f"Undefined variable: {name}")

    def has_var(self, name: str) -> bool:
        """Check if a variable exists."""
        return self.environment.has(name)

    def resolve(self, node: Any) -> Any:
        """Execute an AST node in this context."""
        return self.interpreter.execute(node, self)

    # noinspection PyUnusedLocal
    def frame(
        self,
        file: Optional[str],
        line: Optional[int],
        function: Optional[str],
        column: Optional[int] = None,
        node: Optional[Any] = None,
    ):
        """Create an execution frame for stack tracing."""
        return frame(
            self,
            file or self.current_file,
            line,
            function,
            self.environment.variables,
            node=node,
        )

    def push_scope(self, owner: str, instance: Optional[Any] = None) -> "ExecutionContext":
        """Enter a class or interface scope."""
        ctx = self.child()
        ctx.current_scope_owner = owner
        ctx.current_instance = instance
        return ctx

    def pop_scope(self) -> "ExecutionContext":
        """Exit current scope."""
        return self.parent_context or self

    def can_access_private_member(
        self,
        owner_class: str,
        accessing_instance: Optional[Any] = None,
    ) -> bool:
        """Validate access to a private class member."""
        if self.current_scope_owner == owner_class:
            return True

        if (
            accessing_instance is not None
            and self.current_instance is not None
            and accessing_instance is self.current_instance
        ):
            return True

        return False
