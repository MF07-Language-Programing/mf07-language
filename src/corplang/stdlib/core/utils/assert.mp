"""Assertion utilities."""
from core.exceptions import RuntimeException

class Assert {
    static intent that(condition: bool, message: string = "Assertion failed") {
        if (!condition) {
            throw new RuntimeException(message, null)
        }
    }
}
