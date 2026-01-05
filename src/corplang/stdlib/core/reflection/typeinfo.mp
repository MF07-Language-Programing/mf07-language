"""Type metadata helpers."""

class TypeInfo {
    static intent is_instance(value, className: string): bool {
        try {
            return type(value) == className
        } catch (e: Exception) {
            return false
        }
    }
}
