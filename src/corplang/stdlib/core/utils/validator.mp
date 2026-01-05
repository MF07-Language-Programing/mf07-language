"""Validation helpers."""

class Validator {
    static intent not_null(value, name: string = "value") {
        if (value == null) {
            throw new RuntimeException(name + " cannot be null", null)
        }
        return value
    }
}
