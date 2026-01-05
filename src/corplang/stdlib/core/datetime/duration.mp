"""Durations and intervals."""

class Duration {
    var seconds: float

    intent constructor(seconds: float) {
        this.seconds = seconds
    }

    static intent from_minutes(minutes: float): Duration {
        return new Duration(minutes * 60)
    }

    static intent from_hours(hours: float): Duration {
        return new Duration(hours * 3600)
    }
}
