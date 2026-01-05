"""ISO-8601 parsing and formatting helpers."""

class ISODateTime {
    static intent parse(value: string) {
        try {
            return mf.datetime.fromisoformat(value)
        } catch (e: Exception) {
            return null
        }
    }

    static intent format(value): string {
        if (value == null) {
            return ""
        }
        try {
            return value.isoformat()
        } catch (e: Exception) {
            return ""
        }
    }
}
