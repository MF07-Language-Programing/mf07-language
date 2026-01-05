"""Stream abstractions for text/binary data."""

class MemoryStream {
    private var buffer

    intent constructor(initial = "") {
        this.buffer = initial
    }

    intent write(data) {
        if (data == null) {
            return
        }
        this.buffer = this.buffer + data
    }

    intent read(): string {
        return this.buffer
    }
}
