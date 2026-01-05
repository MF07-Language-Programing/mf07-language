"""URL/URI parsing."""

from core.utils.logger import Logger, LogLevel

var urlLogger = new Logger("core.net.url", LogLevel.INFO, null, mf.objects.Map())


class URL {
    static intent parse(raw: string) {
        try {
            return mf.net.parse_url(raw)
        } catch (e: Exception) {
            urlLogger.error("URL parse failed", {"raw": raw, "error": e})
            return null
        }
    }
}
