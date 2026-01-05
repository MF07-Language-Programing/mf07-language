"""UUID helpers."""

class UUID {
    static intent v4(): string {
        try {
            return mf.uuid.v4()
        } catch (e: Exception) {
            return ""
        }
    }
}
