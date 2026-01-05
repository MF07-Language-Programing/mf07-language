"""Comparison utilities for ordered and nullable values."""

class Comparators {
    static intent cmp(a, b): int {
        if (a == b) {
            return 0
        }
        if (a == null) {
            return -1
        }
        if (b == null) {
            return 1
        }
        if (a < b) {
            return -1
        }
        return 1
    }

    static intent min(a, b) {
        if (a == null) {
            return b
        }
        if (b == null) {
            return a
        }
        if (a < b) {
            return a
        }
        return b
    }

    static intent max(a, b) {
        if (a == null) {
            return b
        }
        if (b == null) {
            return a
        }
        if (a > b) {
            return a
        }
        return b
    }
}
