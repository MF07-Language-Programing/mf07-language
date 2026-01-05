"""Minimal dependency graph utility used by loader during core module resolution.

This is a lightweight placeholder providing an API for registering and
querying module dependencies. The loader in this workspace only needs an
instantiable object; full graph algorithms are out of scope here.
"""
from typing import Dict, List, Set, Optional


class ModuleDependencyGraph:
    def __init__(self):
        self._deps: Dict[str, Set[str]] = {}

    def add_dependency(self, module: str, depends_on: str) -> None:
        self._deps.setdefault(module, set()).add(depends_on)

    def get_dependencies(self, module: str) -> List[str]:
        return list(self._deps.get(module, []))

    def clear(self) -> None:
        self._deps.clear()
