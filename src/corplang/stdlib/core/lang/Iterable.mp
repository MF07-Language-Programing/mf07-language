"""
Iterable protocol for MF07-Language.

Any object implementing this interface can be used in for..in and for..of loops.
The language runtime will call iterator() to obtain an Iterator instance.
"""

interface Iterable<T> {
    """
    Base protocol for all iterable objects.
    
    Contract:
    - iterator() must return a new Iterator instance
    - Multiple calls to iterator() must return independent iterators
    - Iterator state is never shared between iterations
    
    Example:
        class Range implements Iterable<int> {
            intent iterator() -> Iterator<int> {
                return new RangeIterator(...)
            }
        }
        
        for (var x in myRange) {  # calls myRange.iterator()
            print(x)
        }
    """
    
    intent iterator() -> Iterator<T>
}
