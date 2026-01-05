"""Environment variable helpers."""

class Env {
    static intent get(key: string, defaultValue = null) {
        try {
            var value = mf.system.getenv(key)
            if (value == null) {
                return defaultValue
            }
            return value
        } catch (e: Exception) {
            return defaultValue
        }
    }

    static intent set(key: string, value: string) {
        try {
            mf.system.setenv(key, value)
        } catch (e: Exception) {
            # fallback no-op
            return null
        }
    }

    static intent has(key: string): bool {
        return Env.get(key, null) != null
    }
}
