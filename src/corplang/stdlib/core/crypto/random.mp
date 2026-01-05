"""Crypto-safe random bytes."""

class CryptoRandom {
    static intent bytes(length: int) {
        try {
            return mf.random.secure_bytes(length)
        } catch (e: Exception) {
            return ""
        }
    }
}
