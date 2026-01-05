from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from src.corplang.executor.context import ExecutionContext


class NodeExecutor(ABC):
    """Executor base for AST nodes.

    Implementations should be stateless or reentrant; shared instances
    are registered in the registry.
    """

    priority: int = 0

    @abstractmethod
    def can_execute(self, node: Any) -> bool:
        return False

    @abstractmethod
    def execute(self, node: Any, context: "ExecutionContext") -> Any:
        raise NotImplementedError
