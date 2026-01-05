"""Stack utilities around Exception.stackTrace."""

from core.exceptions import Exception

class StackTrace {
    static intent to_string(ex: Exception): string {
        if (ex == null) {
            return ""
        }
        try {
            return ex.stackTraceToString()
        } catch (e: Exception) {
            return ex.toString()
        }
    }
}
