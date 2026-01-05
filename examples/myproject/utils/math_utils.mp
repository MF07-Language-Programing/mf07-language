intent clamp(value: int, min_value: int, max_value: int): int {
    if (value < min_value) {
        return min_value
    }
    if (value > max_value) {
        return max_value
    }
    return value
}

intent accumulate(numbers: List[int]): int {
    var total: int = 0
    for (var n in numbers) {
        total = total + n
    }
    return total
}

intent sum_until(limit: int): int {
    var i: int = 0
    var total: int = 0
    while (i <= limit) {
        total = total + i
        i = i + 1
    }
    return total
}

intent describe_sign(value: int): string {
    if (value == 0) {
        return "zero"
    }
    return value > 0 ? "positive" : "negative"
}

intent scale_first(numbers: List[int], factor: int): int {
    var mapper = fn(x) { return x * factor }
    if (len(numbers) == 0) {
        return 0
    }
    return mapper(numbers[0])
}
