"""Minimal ModuleRegistry used by loader and interpreter.

This provides a simple in-memory registry mapping module names and paths
to their exported symbols. It's intentionally small but sufficient for
unit-imports and interpreter boot in this workspace.
"""
from copy import deepcopy
from typing import Any, Dict, Optional


class ModuleRegistry:
    def __init__(self):
        self._by_name: Dict[str, Dict[str, Any]] = {}
        self._by_path: Dict[str, str] = {}

    def register(self, name: str, path: Optional[str], exports: Optional[Dict[str, Any]] = None, loaded_at: Optional[float] = None):
        self._by_name[name] = {"path": path, "exports": deepcopy(exports) if exports is not None else None, "loaded_at": loaded_at}
        if path:
            self._by_path[path] = name

    def is_loaded_by_name(self, name: str) -> bool:
        return name in self._by_name

    def is_loaded_by_path(self, path: str) -> bool:
        return path in self._by_path

    def get_exports_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        rec = self._by_name.get(name)
        return deepcopy(rec.get("exports")) if rec and rec.get("exports") is not None else None

    def get_exports_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        name = self._by_path.get(path)
        if not name:
            return None
        return self.get_exports_by_name(name)
