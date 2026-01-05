"""Executor"""
from typing import Any, TYPE_CHECKING

from src.corplang.core.config import get_logger

if TYPE_CHECKING:
    from src.corplang.executor.context import ExecutionContext

logger = get_logger(__name__)


class Executor:
    """
    Centralized dispatcher for Corplang AST nodes.
    Delegates execution logic to registered executors in the interpreter's registry.
    """

    def __init__(self, interpreter: Any):
        self.interpreter = interpreter

    def execute(self, node: Any, context: "ExecutionContext") -> Any:
        """Execute with context"""
        if node is None:
            return None

        if isinstance(node, (list, tuple)):
            result = None
            for n in node:
                result = self.execute(n, context)
            return result

        try:
            executor = self.interpreter.registry.get_executor(node)
            return executor.execute(node, context)
        except Exception as e:
            if hasattr(self.interpreter, 'execute'):
                return self.interpreter.execute(node, context)
            raise e
