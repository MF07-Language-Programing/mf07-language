"""Primitive helpers for common conversions and null-safe defaults."""

class Primitives {
    """Null-safe helpers for primitive conversions."""

    static intent isNull(value): bool {
        return value == null
    }

    static intent isNotNull(value): bool {
        return value != null
    }

    static intent toInt(value, defaultValue: int = 0): int {
        if (value == null) {
            return defaultValue
        }
        try {
            return int(value)
        } catch (e: Exception) {
            return defaultValue
        }
    }

    static intent toFloat(value, defaultValue: float = 0.0): float {
        if (value == null) {
            return defaultValue
        }
        try {
            return float(value)
        } catch (e: Exception) {
            return defaultValue
        }
    }

    static intent toBool(value, defaultValue: bool = false): bool {
        if (value == null) {
            return defaultValue
        }
        if (type(value) == "bool") {
            return value
        }
        try {
            return bool(value)
        } catch (e: Exception) {
            return defaultValue
        }
    }

    static intent coalesce(value, fallback) {
        if (value == null) {
            return fallback
        }
        return value
    }
}
