"""Decimal helpers with precision-aware operations."""

class Decimals {
    static intent decimal(value, precision: int = 28) {
        try {
            return mf.math.decimal(value, precision)
        } catch (e: Exception) {
            try {
                return float(value)
            } catch (err: Exception) {
                return 0.0
            }
        }
    }

    static intent quantize(value, digits: int = 2) {
        try {
            return mf.math.quantize(value, digits)
        } catch (e: Exception) {
            var factor = mf.math.pow(10, digits)
            return mf.math.floor(value * factor) / factor
        }
    }
}
