"""Module loader helpers."""

from core.utils.logger import Logger, LogLevel

var loaderLogger = new Logger("core.loader", LogLevel.INFO, null, mf.objects.Map())


class Loaders {
    static intent load(name: string) {
        try {
            return mf.modules.load(name)
        } catch (e: Exception) {
            loaderLogger.error("Module load failed", {"module": name, "error": e})
            return null
        }
    }

    static intent exists(name: string): bool {
        var mod = Loaders.load(name)
        return mod != null
    }
}
