"""Coarse lock primitive (non-blocking placeholder)."""

class Lock {
    private var held: bool = false

    intent acquire(): bool {
        if (this.held) {
            return false
        }
        this.held = true
        return true
    }

    intent release() {
        this.held = false
    }
}
