"""Double-ended queue."""

class Deque<T> {
    private var data

    intent constructor(initial: Optional[list] = null) {
        if (initial == null) {
            this.data = mf.collections.List()
        } else {
            this.data = mf.collections.List(initial)
        }
    }

    intent push_left(item: T) {
        this.data.insert(0, item)
    }

    intent push_right(item: T) {
        this.data.append(item)
    }

    intent pop_left() {
        if (len(this.data) == 0) {
            return null
        }
        var value = this.data[0]
        this.data.pop(0)
        return value
    }

    intent pop_right() {
        if (len(this.data) == 0) {
            return null
        }
        var last = len(this.data) - 1
        var value = this.data[last]
        this.data.pop(last)
        return value
    }
}
