"""Boolean helpers for truthy/falsy evaluations."""

class Booleans {
    static intent truthy(value): bool {
        if (value == null) {
            return false
        }
        if (type(value) == "bool") {
            return value
        }
        try {
            return bool(value)
        } catch (e: Exception) {
            return true
        }
    }

    static intent falsy(value): bool {
        return !Booleans.truthy(value)
    }
}
