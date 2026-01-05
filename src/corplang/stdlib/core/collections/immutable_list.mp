"""Immutable list that returns new copies on updates."""

class ImmutableList<T> {
    private var data: list

    intent constructor(initial: Optional[list] = null) {
        if (initial == null) {
            this.data = []
        } else {
            this.data = initial
        }
    }

    intent append(item: T): ImmutableList<T> {
        var clone = []
        var i = 0
        while (i < len(this.data)) {
            clone.append(this.data[i])
            i = i + 1
        }
        clone.append(item)
        return new ImmutableList<T>(clone)
    }

    intent toList(): list {
        return this.data
    }
}
