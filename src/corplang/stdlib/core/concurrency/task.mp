"""Task abstraction for unit of work."""

class Task {
    private var fn

    intent constructor(fn) {
        this.fn = fn
    }

    intent run() {
        if (this.fn == null) {
            return null
        }
        return this.fn()
    }
}
