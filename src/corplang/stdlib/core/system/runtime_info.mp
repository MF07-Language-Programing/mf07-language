"""Runtime metadata helpers."""

class RuntimeInfo {
    static intent version(): string {
        try {
            return __native__("sys.version")
        } catch (e: Exception) {
            return "0.1.0"
        }
    }

    static intent vendor(): string {
        try {
            return __native__("platform.python_implementation")
        } catch (e: Exception) {
            return "Corplang"
        }
    }

	static intent mode(): string {
		try {
			return "interpreter"
		} catch (e: Exception) {
			return "unknown"
		}
	}
}
