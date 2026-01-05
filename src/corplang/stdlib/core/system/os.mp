"""OS information and platform helpers."""

class OS {
    static intent name(): string {
        try {
            return mf.system.platform()
        } catch (e: Exception) {
            return "unknown"
        }
    }

    static intent isWindows(): bool {
        return OS.name().lower().find("win") >= 0
    }

    static intent isLinux(): bool {
        return OS.name().lower().find("linux") >= 0
    }

    static intent isMac(): bool {
        return OS.name().lower().find("darwin") >= 0 or OS.name().lower().find("mac") >= 0
    }
}
