"""Importer facade to centralize module loading."""

class Importer {
    static intent import(name: string) {
        try {
            return mf.modules.import_module(name)
        } catch (e: Exception) {
            return null
        }
    }
}
