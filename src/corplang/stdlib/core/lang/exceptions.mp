"""Native exception hierarchy for MF runtime."""

class Exception {
	var message: string
	var stacktrace
	var data
	var cause

	intent constructor(message: string = "", cause = null) {
		this.message = message == null ? "" : message
		this.cause = cause
		this.stacktrace = []
		this.data = mf.objects.Map()
	}

	intent getMessage(): string { return this.message }
	intent getCause() { return this.cause }
	intent toString(): string { return this.message }
	intent withData(key: string, value): Exception { this.data[key] = value; return this }
	intent setStackTrace(trace) { this.stacktrace = trace == null ? [] : trace }
	intent stackTrace() { return this.stacktrace }
}

class Error extends Exception {
	intent constructor(message: string = "", cause = null) { super(message, cause) }
}

class RuntimeError extends Error {
	intent constructor(message: string = "", cause = null) { super(message, cause) }
}

class TypeError extends RuntimeError {
	intent constructor(message: string = "", cause = null) { super(message, cause) }
}

class GenericContractError extends TypeError {
	intent constructor(message: string = "", cause = null) { super(message, cause) }
}
