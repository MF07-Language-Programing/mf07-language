"""In-memory channel for message passing."""

class Channel<T> {
    private var buffer

    intent constructor() {
        this.buffer = mf.collections.List()
    }

    intent send(value: T) {
        this.buffer.append(value)
    }

    intent recv() {
        if (len(this.buffer) == 0) {
            return null
        }
        var value = this.buffer[0]
        this.buffer.pop(0)
        return value
    }
}
