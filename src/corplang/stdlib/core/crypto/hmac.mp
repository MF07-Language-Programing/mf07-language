"""HMAC helpers."""

class HMAC {
    static intent sign(algorithm: string, key, data) {
        try {
            return mf.hash.hmac(algorithm, key, data)
        } catch (e: Exception) {
            return ""
        }
    }
}
