"""
Security core for Corplang / MF07.

Handles authentication, sandboxing, permissions,
rate limiting, and execution safety.
"""

from __future__ import annotations

import threading
import time
from enum import Enum
from typing import Dict, List, Set, Callable


class SecurityManager:
    """Runtime security, sandboxing, and permission control."""

    class Permission(Enum):
        FILE_READ = "file_read"
        FILE_WRITE = "file_write"
        NETWORK_ACCESS = "network_access"
        SYSTEM_COMMANDS = "system_commands"
        MEMORY_ALLOCATION = "memory_allocation"
        IMPORT_EXTERNAL = "import_external"
        DANGEROUS_OPERATIONS = "dangerous_operations"

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

        # Auth / identity
        self.tokens: Dict[str, str] = {}

        # Abuse control
        self.ip_failures: Dict[str, int] = {}
        self.blocked_ips: Dict[str, float] = {}
        self.rate_limits: Dict[str, List[float]] = {}
        self.requests_per_minute: int = 60
        self.burst_limit: int = 10

        # Permissions
        self._permissions: Set[SecurityManager.Permission] = set()

        # Operation limits
        self._operation_limits: Dict[str, int] = {
            "file_operations": 1000,
            "network_requests": 100,
            "execution_time_seconds": 300,
        }
        self._operation_counts: Dict[str, int] = {}
        self._start_time = time.time()
        self._lock = threading.RLock()

        # Sandboxing
        self.allowed_builtins = {"abs", "min", "max", "len", "sum", "range"}
        self.blocked_names = {
            "__import__", "eval", "exec", "open",
            "compile", "globals", "locals"
        }

        # Observability
        self.audit_log: List[str] = []
        self.event_hooks: Dict[str, List[Callable]] = {}

    def register_token(self, user: str, token: str):
        """Register an auth token for a user."""
        self.tokens[user] = token

    def authenticate(self, token: str) -> bool:
        """Validate authentication token."""
        return token in self.tokens.values()

    @staticmethod
    def authorize(user: str, action: str) -> bool:
        """Authorize user action (hook point)."""
        return True

    def check_rate_limit(self, ip: str) -> bool:
        """Check if an IP is within rate limits."""
        now = time.time()
        times = self.rate_limits.setdefault(ip, [])
        times.append(now)
        self.rate_limits[ip] = [t for t in times if now - t < 60]
        return len(self.rate_limits[ip]) <= self.requests_per_minute

    def block_ip(self, ip: str, duration: int = 300):
        """Block an IP for a duration in seconds."""
        self.blocked_ips[ip] = time.time() + duration

    def is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked."""
        return self.blocked_ips.get(ip, 0) > time.time()

    def enable_permission(self, permission: Permission):
        """Enable a permission."""
        self._permissions.add(permission)

    def disable_permission(self, permission: Permission):
        """Disable a permission."""
        self._permissions.discard(permission)

    def check_permission(self, permission: Permission, operation: str = ""):
        """Validate permission and operation limits."""
        if not self.enabled:
            return

        if permission not in self._permissions:
            raise RuntimeError(f"Permission denied: {permission.value}")

        self._check_operation_limits(operation)

    def _check_operation_limits(self, operation: str):
        """Check execution and operation limits."""
        with self._lock:
            elapsed = time.time() - self._start_time
            if elapsed > self._operation_limits["execution_time_seconds"]:
                raise RuntimeError("Execution time limit exceeded")

            if not operation:
                return

            count = self._operation_counts.get(operation, 0) + 1
            self._operation_counts[operation] = count

            limit = self._operation_limits.get(operation)
            if limit and count > limit:
                raise RuntimeError(f"Operation limit exceeded: {operation}")

    def validate_var_name(self, name: str) -> bool:
        """Validate variable or symbol name."""
        if not name.isidentifier() or name in self.blocked_names:
            self.audit(f"Invalid name: {name}")
            return False
        return True

    # noinspection PyUnresolvedReferences
    def sandbox_exec(self, code: str, context: dict):
        """Execute code in a restricted environment."""
        safe_builtins = {
            k: __builtins__[k]
            for k in self.allowed_builtins
            if k in __builtins__
        }
        context["__builtins__"] = safe_builtins
        try:
            exec(code, context)
        except Exception as e:
            self.audit(f"Sandbox error: {e}")
            raise

    @staticmethod
    def protect_loops(max_iterations: int = 100_000):
        """Generator to guard against infinite loops."""
        def guard():
            count = 0
            while True:
                count += 1
                if count > max_iterations:
                    raise RuntimeError("Max loop iterations exceeded")
                yield
        return guard

    def audit(self, message: str):
        """Log a security event."""
        self.audit_log.append(message)

    def add_event_hook(self, event: str, callback: Callable):
        """Register a security event hook."""
        self.event_hooks.setdefault(event, []).append(callback)

    def trigger_event(self, event: str, *args, **kwargs):
        """Trigger registered hooks for an event."""
        for cb in self.event_hooks.get(event, []):
            cb(*args, **kwargs)


security_manager = SecurityManager()
