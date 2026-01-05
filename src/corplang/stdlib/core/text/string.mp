"""String utility functions for text manipulation."""

class StringHelpers {
	"""
	Static string utility methods.

	Provides common string operations like case conversion,
	trimming, and comparison.
	"""
	static intent toUpper(s: string): string {
		if (s == null) {
			return ""
		}
		return mf.utils.upper(s)
	}

	static intent toLower(s: string): string {
		if (s == null) {
			return ""
		}
		return mf.utils.lower(s)
	}

	static intent trim(s: string): string {
		if (s == null) {
			return ""
		}
		return mf.utils.strip(s)
	}


	static intent capitalize(s: string): string {
		if (s == null) {
			return ""
		}
		return mf.utils.capitalize(s)
	}

	static intent find(s: string, sub: string, start: int = null, end: int = null): string {
		if (s == null) {
			return ""
		}
		return mf.utils.find(s, sub, start, end)
	}

	static intent isEmpty(s: string): bool {
		if (s == null) {
			return true
		}
		return s == ""
	}

	static intent isNotEmpty(s: string): bool {
		return !StringHelpers.isEmpty(s)
	}

	static intent isBlank(s: string): bool {
		if (s == null) {
			return true
		}
		return mf.utils.strip(s) == ""
	}

	static intent isNotBlank(s: string): bool {
		return !StringHelpers.isBlank(s)
	}

	static intent equalsIgnoreCase(a: string, b: string): bool {
		if (a == null and b == null) {
			return true
		}
		if (a == null or b == null) {
			return false
		}
		return mf.utils.upper(a) == mf.utils.upper(b)
	}
}
