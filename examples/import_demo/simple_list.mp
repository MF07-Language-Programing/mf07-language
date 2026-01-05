"""Simple List implementation for testing imports."""

class SimpleList {
    private var data
    private var count: int

    intent constructor() {
        this.data = []
        this.count = 0
    }

    intent append(value) {
        this.data.append(value)
        this.count = this.count + 1
    }

    intent get(index: int) {
        if (index >= 0 and index < this.count) {
            return this.data[index]
        }
        return null
    }

    intent length(): int {
        return this.count
    }

    intent toList() {
        return this.data
    }
}
