"""
Utility for managing object relations (e.g., AST, ORM, dependencies).
Maps simple and complex relations. Easy to extend and maintain.
"""

from typing import Dict, List, Any


class Relations:
    """Manages object relations, dependencies, and scope trees."""

    def __init__(self):
        """Initialize relations, dependencies, and scope tree."""
        self.relations: Dict[str, List[Any]] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.scope_tree: Dict[str, List[str]] = {}

    def add(self, key: str, value: Any):
        """Add a value to a relation key."""
        self.relations.setdefault(key, []).append(value)

    def get(self, key: str) -> List[Any]:
        """Get all values for a relation key."""
        return self.relations.get(key, [])

    def remove(self, key: str, value: Any):
        """Remove a value from a relation key."""
        if key in self.relations:
            self.relations[key] = [v for v in self.relations[key] if v != value]

    def add_dependency(self, item: str, depends_on: str):
        """Track that item depends on another item."""
        self.dependencies.setdefault(item, []).append(depends_on)

    def has_circular_dependency(self, item: str, visited=None) -> bool:
        """Detect circular dependencies for an item."""
        if visited is None:
            visited = set()
        if item in visited:
            return True
        visited.add(item)
        for dep in self.dependencies.get(item, []):
            if self.has_circular_dependency(dep, visited):
                return True
        visited.remove(item)
        return False

    def add_scope(self, parent: str, child: str):
        """Add a child scope to a parent scope."""
        self.scope_tree.setdefault(parent, []).append(child)

    def get_children(self, parent: str) -> List[str]:
        """Get all child scopes of a parent."""
        return self.scope_tree.get(parent, [])

relations = Relations()
