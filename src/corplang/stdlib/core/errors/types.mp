"""Typed errors for common failure modes."""

from core.exceptions import Exception

class ArgumentError extends Exception {
    intent constructor(message: string, cause = null) {
        super(message, cause)
    }
}

class IOError extends Exception {
    intent constructor(message: string, cause = null) {
        super(message, cause)
    }
}
