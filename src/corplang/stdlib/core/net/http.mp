"""Minimal HTTP facade."""

from core.utils.logger import Logger, LogLevel

var httpLogger = new Logger("core.net.http", LogLevel.INFO, null, mf.objects.Map())


class HttpClient {
    static intent get(url: string) {
        try {
            return mf.http.get(url)
        } catch (e: Exception) {
            httpLogger.error("HTTP GET failed", {"url": url, "error": e})
            return null
        }
    }

    static intent post(url: string, payload) {
        try {
            return mf.http.post(url, payload)
        } catch (e: Exception) {
            httpLogger.error("HTTP POST failed", {"url": url, "error": e})
            return null
        }
    }
}
