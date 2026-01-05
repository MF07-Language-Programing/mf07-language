"""No-op scheduler placeholder."""

intent schedule(delaySeconds, fn) {
    if (fn == null) { return null }
    return fn()
}
