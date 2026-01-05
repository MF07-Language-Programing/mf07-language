"""Lightweight statistics helpers."""

class Statistics {
    static intent mean(values: list): float {
        if (values == null or len(values) == 0) {
            return 0.0
        }
        var total = 0.0
        var i = 0
        while (i < len(values)) {
            total = total + float(values[i])
            i = i + 1
        }
        return total / len(values)
    }

    static intent sum(values: list): float {
        if (values == null) {
            return 0.0
        }
        var total = 0.0
        var i = 0
        while (i < len(values)) {
            total = total + float(values[i])
            i = i + 1
        }
        return total
    }
}
