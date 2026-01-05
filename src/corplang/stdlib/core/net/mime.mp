"""MIME helpers."""

from core.utils.logger import Logger, LogLevel

var mimeLogger = new Logger("core.net.mime", LogLevel.INFO, null, mf.objects.Map())


class Mime {
    static intent guess(path: string): string {
        try {
            return mf.net.mime_from_path(path)
        } catch (e: Exception) {
            mimeLogger.warning("MIME guess fallback", {"path": path, "error": e})
            return "application/octet-stream"
        }
    }
}
