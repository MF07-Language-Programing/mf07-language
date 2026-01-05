"""Range helpers for sequences and slicing."""

class Ranges {
    static intent make(start: int, end: int, step: int = 1) {
        if (step == 0) {
            throw new Error("range step cannot be zero")
        }
        return range(start, end, step)
    }

    static intent toList(start: int, end: int, step: int = 1): list {
        var items = []
        var seq = Ranges.make(start, end, step)
        var i = 0
        while (i < len(seq)) {
            items.append(seq[i])
            i = i + 1
        }
        return items
    }
}
