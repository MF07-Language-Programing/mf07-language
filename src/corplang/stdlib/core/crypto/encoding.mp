"""Base encodings (base64/base32)."""

class BaseEncoding {
    static intent b64_encode(data): string {
        try {
            return mf.hash.base64_encode(data)
        } catch (e: Exception) {
            return ""
        }
    }

    static intent b64_decode(data) {
        try {
            return mf.hash.base64_decode(data)
        } catch (e: Exception) {
            return ""
        }
    }

    static intent b32_encode(data): string {
        try {
            return mf.hash.base32_encode(data)
        } catch (e: Exception) {
            return ""
        }
    }
}
