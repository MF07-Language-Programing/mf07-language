"""Exception handling classes for error management."""

from core.utils.logger import Logger, LogLevel

var errorLogger = new Logger("core.errors", LogLevel.ERROR, null, mf.objects.Map())

class Exception {
	var message: string
	var cause
	var stackTrace

	intent constructor(message: string, cause) {
		if (message == null) {
			message = ""
		}
		this.message = message
		this.cause = cause
		this.stackTrace = new List([])
	}

	intent getMessage(): string {
		return this.message
	}

	intent getCause() {
		return this.cause
	}

	intent _attachStackTrace(frames) {
		if (frames == null) {
			this.stackTrace = new List([])
			return
		}
		if (type(frames) == "InstanceObject") {
			this.stackTrace = frames
			return
		}
		this.stackTrace = new List(frames)
	}

	intent stackTraceList() {
		if (this.stackTrace == null) {
			this.stackTrace = new List([])
		}
		return this.stackTrace
	}

	intent stackTraceToString(): string {
		var trace = this.stackTraceList()
		if (len(trace) == 0) {
			return ""
		}
		var buffer = ""
		var i = 0
		while (i < len(trace)) {
			var frame = trace[i]
			if (type(frame) == "InstanceObject") {
				frame = frame.__raw__()
			}
			var functionName = "<unknown>"
			if (mf.objects.mapHas(frame, "function")) {
				var maybeFn = frame["function"]
				if (maybeFn != null and maybeFn != "") {
					functionName = maybeFn
				}
			}
			var file = ""
			if (mf.objects.mapHas(frame, "file") and frame["file"] != null) {
				file = frame["file"]
			}
			var lineInfo = ""
			if (mf.objects.mapHas(frame, "line") and frame["line"] != null) {
				lineInfo = frame["line"].toString()
			}
			var entry = functionName
			if (file != "") {
				entry = entry + " (" + file
				if (lineInfo != "") {
					entry = entry + ":" + lineInfo
				}
				entry = entry + ")"
			}
			if (buffer != "") {
				buffer = buffer + "\n"
			}
			"""Compatibility layer that re-exports native exceptions."""

			from core.lang.exceptions import Exception, Error, RuntimeError, TypeError, GenericContractError

			# Legacy alias kept for modules that still reference RuntimeException
			class RuntimeException extends RuntimeError {
				intent constructor(message: string = "", cause = null) { super(message, cause) }
			}
		if (msg == null or msg == "") {
