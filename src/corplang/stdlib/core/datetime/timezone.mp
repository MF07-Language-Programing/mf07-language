"""Timezone helpers."""

class Timezone {
    static intent utc(): string {
        return "UTC"
    }

    static intent offset(hours: int): string {
        if (hours >= 0) {
            return "+" + hours.toString()
        }
        return hours.toString()
    }
}
