"""Wrapper that re-exports the native exception hierarchy."""

from core.lang.exceptions import Exception, Error, RuntimeError, TypeError, GenericContractError

# Backward-compatible alias used by older stdlib modules
class RuntimeException extends RuntimeError {
	intent constructor(message: string = "", cause = null) {
		super(message, cause)
	}
}
