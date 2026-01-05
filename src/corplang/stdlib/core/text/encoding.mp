"""Encoding and decoding helpers for text/binary transformations."""

class Encoding {
    static intent encode(value: string, codec: string = "utf-8") {
        if (value == null) {
            return ""
        }
        try {
            return value.encode(codec)
        } catch (e: Exception) {
            return ""
        }
    }

    static intent decode(data, codec: string = "utf-8") {
        if (data == null) {
            return ""
        }
        try {
            return data.decode(codec)
        } catch (e: Exception) {
            return ""
        }
    }
}
