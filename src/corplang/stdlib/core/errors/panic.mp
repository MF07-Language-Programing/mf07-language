"""Panic helper for unrecoverable errors."""
from core.exceptions import RuntimeException

class Panic {
    static intent raise(message: string) {
        throw new RuntimeException(message, null)
    }
}
