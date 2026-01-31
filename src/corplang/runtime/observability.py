"""Observability hooks for node execution tracking."""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List, Callable
from time import perf_counter
from enum import Enum


class NodeEventType(Enum):
    """Node execution lifecycle events."""
    BEFORE_EXECUTE = "before_execute"
    AFTER_EXECUTE = "after_execute"
    ERROR = "error"


@dataclass
class NodeEvent:
    """Immutable execution event for observability."""
    
    event_type: NodeEventType
    node_type: str
    node: Any  # AST node
    file_path: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    
    # Execution metrics
    elapsed_seconds: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None
    
    # Context snapshot
    context_vars: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize event for logging or export."""
        return {
            "event": self.event_type.value,
            "node_type": self.node_type,
            "file": self.file_path,
            "line": self.line,
            "elapsed": self.elapsed_seconds,
            "error": str(self.error) if self.error else None
        }


class ObservabilityManager:
    """Central registry for execution observers."""
    
    def __init__(self):
        self._observers: List[Callable[[NodeEvent], None]] = []
        self._enabled = True
    
    def register(self, callback: Callable[[NodeEvent], None]) -> None:
        """Register an observer callback."""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def unregister(self, callback: Callable[[NodeEvent], None]) -> None:
        """Remove an observer callback."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def emit(self, event: NodeEvent) -> None:
        """Emit event to all registered observers."""
        if not self._enabled:
            return
        
        for observer in self._observers:
            try:
                observer(event)
            except Exception:
                # Observers must not break execution
                pass
    
    def enable(self) -> None:
        """Enable event emission."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable event emission."""
        self._enabled = False
    
    def clear(self) -> None:
        """Remove all observers."""
        self._observers.clear()


# Global singleton
_observability_manager = ObservabilityManager()


def get_observability_manager() -> ObservabilityManager:
    """Get the global observability manager."""
    return _observability_manager


class ExecutionTracker:
    """Context manager for tracking node execution."""
    
    def __init__(self, node: Any, manager: ObservabilityManager):
        self.node = node
        self.manager = manager
        self.start_time = None
        self.result = None
        self.error = None
    
    def __enter__(self):
        """Emit BEFORE_EXECUTE event."""
        self.start_time = perf_counter()
        
        event = NodeEvent(
            event_type=NodeEventType.BEFORE_EXECUTE,
            node_type=type(self.node).__name__,
            node=self.node,
            file_path=getattr(self.node, "file_path", None),
            line=getattr(self.node, "line", None),
            column=getattr(self.node, "column", None)
        )
        
        self.manager.emit(event)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Emit AFTER_EXECUTE or ERROR event."""
        elapsed = perf_counter() - self.start_time if self.start_time else None
        
        if exc_type:
            event = NodeEvent(
                event_type=NodeEventType.ERROR,
                node_type=type(self.node).__name__,
                node=self.node,
                file_path=getattr(self.node, "file_path", None),
                line=getattr(self.node, "line", None),
                column=getattr(self.node, "column", None),
                elapsed_seconds=elapsed,
                error=exc_val
            )
        else:
            event = NodeEvent(
                event_type=NodeEventType.AFTER_EXECUTE,
                node_type=type(self.node).__name__,
                node=self.node,
                file_path=getattr(self.node, "file_path", None),
                line=getattr(self.node, "line", None),
                column=getattr(self.node, "column", None),
                elapsed_seconds=elapsed,
                result=self.result
            )
        
        self.manager.emit(event)
        return False  # Don't suppress exceptions


def track_execution(node: Any) -> ExecutionTracker:
    """Create execution tracker for a node."""
    return ExecutionTracker(node, get_observability_manager())
