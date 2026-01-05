"""
Collection protocol for MF07-Language.

Base interface for all collection types. Extends Iterable.
"""

from core.lang.Iterable import Iterable

interface Collection<T> extends Iterable<T> {
    """
    Universal contract for collections.
    
    All collections must:
    - Be iterable (inherit from Iterable)
    - Provide size information
    - Support containment checks
    - Allow clearing
    
    Collections are mutable by default. For immutable variants,
    see core.collections.immutable.*.
    
    Example:
        class MyCollection<T> implements Collection<T> {
            intent size() -> int { return this._size }
            intent isEmpty() -> bool { return this.size() == 0 }
            intent clear() { this._data = [] }
            intent contains(value: T) -> bool { ... }
            intent iterator() -> Iterator<T> { ... }
        }
    """
    
    intent size() -> int
    intent isEmpty() -> bool
    intent clear()
    intent contains(value: T) -> bool
}
