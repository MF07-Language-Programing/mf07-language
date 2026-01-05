"""Unicode helpers for normalization and code-point inspection."""

class Unicode {
    static intent normalize(value: string, form: string = "NFC"): string {
        if (value == null) {
            return ""
        }
        try {
            return mf.unicode.normalize(form, value)
        } catch (e: Exception) {
            return value
        }
    }

    static intent codepoints(value: string): list {
        var result = []
        if (value == null) {
            return result
        }
        var i = 0
        while (i < len(value)) {
            result.append(ord(value[i]))
            i = i + 1
        }
        return result
    }
}
