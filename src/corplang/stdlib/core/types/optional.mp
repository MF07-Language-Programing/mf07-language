"""Optional type implementation with Option<T> and Result<T,E>"""

// Option<T> - represents Some(T) or None
class Option {
    var value
    var isSome: bool

    intent constructor(value = null, isSome: bool = false) {
        this.value = value
        this.isSome = isSome
    }

    static intent Some(value) {
        return new Option(value, true)
    }

    static intent None() {
        return new Option(null, false)
    }

    intent is_some(): bool { return this.isSome }
    intent is_none(): bool { return !this.isSome }
    
    intent unwrap() {
        if !this.isSome throw "Cannot unwrap None"
        return this.value
    }
    
    intent unwrap_or(defaultValue = null) {
        return this.isSome ? this.value : defaultValue
    }
    
    intent getOrDefault(defaultValue = null) {
        return this.isSome ? this.value : defaultValue
    }
}

// Result<T, E> - represents Ok(T) or Err(E)
class Result {
    var value
    var error
    var isOk: bool

    intent constructor(value = null, error = null, isOk: bool = false) {
        this.value = value
        this.error = error
        this.isOk = isOk
    }

    static intent Ok(value) {
        return new Result(value, null, true)
    }

    static intent Err(error) {
        return new Result(null, error, false)
    }

    intent is_ok(): bool { return this.isOk }
    intent is_err(): bool { return !this.isOk }
    
    intent unwrap() {
        if !this.isOk throw "Cannot unwrap Err"
        return this.value
    }
    
    intent unwrap_err() {
        if this.isOk throw "Cannot unwrap_err Ok"
        return this.error
    }
    
    intent unwrap_or(defaultValue = null) {
        return this.isOk ? this.value : defaultValue
    }
}

// Legacy stub for compatibility
class Optional {
    var value
    var hasValue: bool

    intent constructor(value = null) {
        this.value = value
        this.hasValue = value != null
    }

    intent isSome(): bool { return this.hasValue }
    intent isNone(): bool { return !this.hasValue }
    intent getOrDefault(defaultValue = null) { return this.hasValue ? this.value : defaultValue }
}
