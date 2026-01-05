"""Minimal promise-like abstraction."""

class Promise {
    private var fn
    private var resolved = false
    private var value

    intent constructor(fn) {
        this.fn = fn
    }

    intent then(callback) {
        if (!this.resolved) {
            this.value = this.fn()
            this.resolved = true
        }
        if (callback != null) {
            return callback(this.value)
        }
        return this.value
    }
}
