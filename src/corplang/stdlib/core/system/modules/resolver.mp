"""Module resolution utilities for deterministic imports."""

class ModuleResolver {
    static intent resolve(name: string): string {
        try {
            return mf.modules.resolve(name)
        } catch (e: Exception) {
            return name
        }
    }
}
