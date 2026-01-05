"""
Memory management utilities for Corplang / MF07.

Provides basic memory monitoring, scope-based object tracking,
optional runtime type checking, and cleanup hooks.
"""

from __future__ import annotations

import sys
import tracemalloc
import weakref
from typing import Any, Optional, Dict, List, Callable

# Enable memory tracking at once
tracemalloc.start()


class MemoryManager:
    """Manages interpreter memory usage and scope object limits."""

    def __init__(
        self,
        limit_mb: Optional[int] = None,
        max_objects_per_scope: int = 1000,
    ):
        """Initialize the memory manager with optional limits."""
        self.limit_mb = limit_mb
        self.max_objects_per_scope = max_objects_per_scope

        self.allocated: int = 0
        self.scope_objects: Dict[str, List[Any]] = {}
        self.cleanup_hooks: List[Callable[[str], None]] = []

        self.type_checks_enabled: bool = True

    def check_memory(self):
        """Return current and peak memory usage (bytes)."""
        current, peak = tracemalloc.get_traced_memory()

        if self.limit_mb and current > self.limit_mb * 1024 * 1024:
            raise MemoryError(
                f"Memory limit exceeded: {current / 1024 / 1024:.2f} MB"
            )

        return current, peak

    @staticmethod
    def log_object(obj: Any, label: str = "obj"):
        """Log approximate object size in bytes."""
        print(f"[MEMORY] {label}: {sys.getsizeof(obj)} bytes")

    def register_object(self, scope: str, obj: Any):
        """Register an object in a scope and enforce limits."""
        objects = self.scope_objects.setdefault(scope, [])
        objects.append(obj)

        if len(objects) > self.max_objects_per_scope:
            raise MemoryError(f"Object limit exceeded in scope: {scope}")

    # noinspection PyBroadException
    def cleanup_scope(self, scope: str):
        """Remove all objects tracked under a scope."""
        self.scope_objects.pop(scope, None)

        for hook in self.cleanup_hooks:
            try:
                hook(scope)
            except Exception:
                pass

    def add_cleanup_hook(self, callback: Callable[[str], None]):
        """Register a callback triggered on scope cleanup."""
        self.cleanup_hooks.append(callback)

    def check_type(self, obj: Any, expected_type: type) -> bool:
        """Validate an object type if checks are enabled."""
        if self.type_checks_enabled and not isinstance(obj, expected_type):
            raise TypeError(
                f"Type mismatch: expected {expected_type}, got {type(obj)}"
            )
        return True


memory_manager = MemoryManager()


def track_object(obj: Any, label: str = "obj"):
    """Log an object and return a weak reference."""
    memory_manager.log_object(obj, label)
    return weakref.ref(obj)
