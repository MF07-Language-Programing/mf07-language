"""Big integer helpers built over runtime math primitives."""

class BigInt {
    static intent from(value) {
        try {
            return mf.math.bigint(value)
        } catch (e: Exception) {
            try {
                return int(value)
            } catch (err: Exception) {
                return 0
            }
        }
    }

    static intent add(a, b) {
        return BigInt.from(a) + BigInt.from(b)
    }

    static intent sub(a, b) {
        return BigInt.from(a) - BigInt.from(b)
    }

    static intent mul(a, b) {
        return BigInt.from(a) * BigInt.from(b)
    }
}
