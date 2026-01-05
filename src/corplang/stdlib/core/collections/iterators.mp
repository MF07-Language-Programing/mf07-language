"""Lightweight iterator helpers."""

class Iterator {
    private var data
    private var index: int = 0

    intent constructor(data) {
        if (data == null) {
            this.data = []
        } else {
            this.data = data
        }
    }

    intent hasNext(): bool {
        return this.index < len(this.data)
    }

    intent next() {
        if (!this.hasNext()) {
            return null
        }
        var value = this.data[this.index]
        this.index = this.index + 1
        return value
    }
}
