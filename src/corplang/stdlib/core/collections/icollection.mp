# core/collections/icollection.mp
# Interface base para todas as coleções do sistema MF07
"""Collection interfaces and base classes for type-safe collections."""

interface ICollection<T> {
    """
    Base interface for all collection types.
    
    Provides core collection methods: size, isEmpty, clear, contains, toArray.
    """
    # Métodos básicos obrigatórios
    intent size() -> int
    intent isEmpty() -> bool  
    intent clear()
    intent contains(value: T) -> bool
    intent toArray() -> Array<T>
    
    # Métodos de iteração
    intent get(index: int) -> T
    intent length() -> int
}

interface IComparable<T> {
    """
    Interface for comparable objects.
    
    Enables sorting and comparison operations.
    """
    intent compareTo(other: T) -> int
    intent equals(other: T) -> bool
    intent hashCode() -> int
}

interface IIterable<T> {
    """
    Interface for iterable collections.
    
    Provides iterator for traversing collection elements.
    """
    intent iterator() -> Iterator<T>
}

# Interface para embeddings e IA
interface IEmbeddable<T> {
    """
    Interface for AI-powered collections with embeddings.
    
    Enables semantic search and similarity operations.
    """
    intent embed(item: T) -> Vector<float>
    intent findSimilar(item: T, threshold: float = 0.8) -> List<T>
    intent updateEmbedding(index: int, item: T)
    intent getEmbedding(index: int) -> Vector<float>
}

# Classe base abstrata para todas as coleções
abstract class BaseCollection<T> implements ICollection<T> {
    """
    Abstract base class for all collections.
    
    Provides common functionality: type validation, AI enablement.
    
    Attributes:
        elementType: Expected element type name
        aiEnabled: Whether AI features are enabled
    """
    protected var elementType: string
    protected var aiEnabled: bool = false
    
    intent constructor(elementType: string) {
        """
        Creates base collection with type.
        
        Args:
            elementType: Element type name
        """
        this.elementType = elementType
    }
    
    # Implementação padrão para isEmpty
    intent isEmpty() -> bool {
        """
        Checks if collection is empty.
        
        Returns:
            True if size is 0
        """
        return this.size() == 0
    }
    
    # Validação de tipos
    protected intent validateType(item: T) -> bool {
        """
        Validates item type matches expected type.
        
        Args:
            item: Item to validate
        
        Returns:
            True if valid (currently always returns true)
        """
        # TODO: Implementar validação em runtime
        return true
    }
    
    # Suporte a IA
    intent enableAI() {
        """
        Enables AI features for this collection.
        
        Example:
            myList.enableAI()
        """
        this.aiEnabled = true
    }
    
    intent isAIEnabled() -> bool {
        """
        Checks if AI features are enabled.
        
        Returns:
            True if AI is enabled
        """
        return this.aiEnabled
    }
}