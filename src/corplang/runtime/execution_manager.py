"""Execution manager for stateful runtime without recompilation."""

from typing import Any, Optional, Dict
from pathlib import Path

from src.corplang.executor.interpreter import Interpreter
from src.corplang.executor.context import ExecutionContext, Environment
from src.corplang.runtime.observability import get_observability_manager, track_execution


class ExecutionManager:
    """Manages stateful execution of compiled AST without recompilation."""
    
    def __init__(self, interpreter: Interpreter):
        """
        Initialize with an existing interpreter instance.
        
        Args:
            interpreter: Pre-configured Interpreter with registered executors
        """
        self.interpreter = interpreter
        self._root_environment = Environment()
        self._observability = get_observability_manager()
        self._execution_count = 0
    
    def create_context(
        self,
        file_path: Optional[str] = None,
        initial_vars: Optional[Dict[str, Any]] = None
    ) -> ExecutionContext:
        """
        Create a reusable execution context.
        
        Args:
            file_path: Source file path for debugging
            initial_vars: Initial variable definitions
        
        Returns:
            ExecutionContext ready for execution
        """
        env = Environment(parent=self._root_environment)
        
        if initial_vars:
            for name, value in initial_vars.items():
                env.define(name, value)
        
        return ExecutionContext(
            interpreter=self.interpreter,
            environment=env,
            memory_manager=None,
            security_manager=None,
            pattern_matcher=None,
            current_file=file_path
        )
    
    def execute_node(
        self,
        node: Any,
        context: ExecutionContext,
        observe: bool = True
    ) -> Any:
        """
        Execute a single AST node with optional observability.
        
        Args:
            node: Compiled AST node
            context: Execution context with state
            observe: Enable observability hooks
        
        Returns:
            Node execution result
        """
        if observe:
            with track_execution(node) as tracker:
                result = self.interpreter.execute(node, context)
                tracker.result = result
                self._execution_count += 1
                return result
        else:
            result = self.interpreter.execute(node, context)
            self._execution_count += 1
            return result
    
    def execute_nodes(
        self,
        nodes: list,
        context: ExecutionContext,
        observe: bool = True
    ) -> Any:
        """
        Execute multiple AST nodes sequentially with shared context.
        
        Args:
            nodes: List of compiled AST nodes
            context: Shared execution context
            observe: Enable observability hooks
        
        Returns:
            Last node execution result
        """
        result = None
        for node in nodes:
            result = self.execute_node(node, context, observe=observe)
        return result
    
    def execute_program(
        self,
        program_node: Any,
        context: Optional[ExecutionContext] = None,
        observe: bool = True
    ) -> Any:
        """
        Execute a complete Program AST node.
        
        Args:
            program_node: Program AST with statements
            context: Optional execution context (created if None)
            observe: Enable observability hooks
        
        Returns:
            Last statement result
        """
        if context is None:
            file_path = getattr(program_node, "file_path", None)
            context = self.create_context(file_path=file_path)
        
        statements = getattr(program_node, "statements", [])
        return self.execute_nodes(statements, context, observe=observe)
    
    def get_environment_snapshot(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Capture current environment state.
        
        Args:
            context: Execution context to snapshot
        
        Returns:
            Dictionary of all defined variables
        """
        snapshot = {}
        env = context.environment
        
        while env:
            snapshot.update(env.variables)
            env = env.parent
        
        return snapshot
    
    def reset_root_environment(self) -> None:
        """Clear root environment state."""
        self._root_environment = Environment()
    
    @property
    def execution_count(self) -> int:
        """Total nodes executed by this manager."""
        return self._execution_count
    
    @property
    def observability(self):
        """Access observability manager."""
        return self._observability
