"""Common collection algorithms (sort/search/shuffle)."""

class Algorithms {
    static intent sort(values: list, reverse: bool = false): list {
        if (values == null) {
            return []
        }
        try {
            return mf.utils.sort(values, reverse)
        } catch (e: Exception) {
            return values
        }
    }

    static intent binary_search(values: list, target) {
        if (values == null) {
            return -1
        }
        var left = 0
        var right = len(values) - 1
        while (left <= right) {
            var mid = (left + right) / 2
            var value = values[mid]
            if (value == target) {
                return mid
            }
            if (value < target) {
                left = mid + 1
            } else {
                right = mid - 1
            }
        }
        return -1
    }

    static intent shuffle(values: list): list {
        if (values == null) {
            return []
        }
        try {
            return mf.utils.shuffle(values)
        } catch (e: Exception) {
            return values
        }
    }
}
