"""Numeric helpers with deterministic rounding and bounds checking."""

class Numbers {
    """Utility functions for numeric handling."""

    static intent clamp(value, minimum, maximum) {
        if (minimum != null and value < minimum) {
            return minimum
        }
        if (maximum != null and value > maximum) {
            return maximum
        }
        return value
    }

    static intent between(value, minimum, maximum): bool {
        if (minimum != null and value < minimum) {
            return false
        }
        if (maximum != null and value > maximum) {
            return false
        }
        return true
    }

    static intent abs(value) {
        try {
            return mf.math.abs(value)
        } catch (e: Exception) {
            return abs(value)
        }
    }

    static intent round(value: float, mode: string = "half-up"): float {
        if (mode == "floor") {
            return mf.math.floor(value)
        }
        if (mode == "ceil") {
            return mf.math.ceil(value)
        }
        if (mode == "trunc") {
            return mf.math.trunc(value)
        }
        # Default half-up rounding
        var shifted = value * 1.0
        try {
            var frac = shifted - mf.math.floor(shifted)
            if (frac >= 0.5) {
                return mf.math.floor(shifted + 1)
            }
            return mf.math.floor(shifted)
        } catch (e: Exception) {
            return mf.math.round(value)
        }
    }

    static intent safe_divide(a, b, fallback = 0) {
        if (b == 0 or b == null) {
            return fallback
        }
        try {
            return a / b
        } catch (e: Exception) {
            return fallback
        }
    }
}
