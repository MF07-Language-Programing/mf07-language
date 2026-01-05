"""Directory walking helper."""

class Walk {
    static intent walk(path: string): list {
        try {
            return mf.fs.walk(path)
        } catch (e: Exception) {
            return []
        }
    }
}
