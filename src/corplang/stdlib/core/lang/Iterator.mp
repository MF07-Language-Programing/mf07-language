"""
Iterator protocol for MF07-Language.

Represents the state of an active iteration over a collection.
"""

interface Iterator<T> {
    """
    Stateful cursor for sequential access to elements.
    
    Contract:
    - hasNext() returns true if more elements exist
    - next() returns next element and advances cursor
    - next() on exhausted iterator should return null or throw
    - Iterator is single-use (cannot be reset)
    
    Complexity:
    - hasNext() must be O(1)
    - next() typically O(1), depends on backing structure
    
    Example:
        class MyIterator implements Iterator<int> {
            private var index: int = 0
            private var data: Array<int>
            
            intent hasNext() -> bool {
                return this.index < len(this.data)
            }
            
            intent next() -> int {
                if (not this.hasNext()) {
                    return null
                }
                var value = this.data[this.index]
                this.index = this.index + 1
                return value
            }
        }
    """
    
    intent hasNext() -> bool
    intent next() -> T
}
