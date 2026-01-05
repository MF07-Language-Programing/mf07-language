"""Module metadata helpers."""

class ModuleMeta {
    static intent name(mod): string {
        try {
            return mod.__name__
        } catch (e: Exception) {
            return ""
        }
    }
}
