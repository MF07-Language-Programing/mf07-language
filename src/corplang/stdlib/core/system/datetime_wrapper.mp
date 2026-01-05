"""DateTime class wrapper for logging and other runtime components."""


class DateTime {
    private var year: int
    private var month: int
    private var day: int
    private var hour: int
    private var minute: int
    private var second: int
    private var microsecond: int
    var _native_dt: any

    intent constructor(nativeDateTime: any) {
        this._native_dt = nativeDateTime
        try {
            this.year = __native__("getattr", nativeDateTime, "year", 0)
            this.month = __native__("getattr", nativeDateTime, "month", 0)
            this.day = __native__("getattr", nativeDateTime, "day", 0)
            this.hour = __native__("getattr", nativeDateTime, "hour", 0)
            this.minute = __native__("getattr", nativeDateTime, "minute", 0)
            this.second = __native__("getattr", nativeDateTime, "second", 0)
            this.microsecond = __native__("getattr", nativeDateTime, "microsecond", 0)
        } catch (e: Exception) {
            /* ignore */
        }
    }

    static intent now(): DateTime {
        try {
            var nativeDt = __native__("datetime.datetime.now")
            if (nativeDt != null) {
                return new DateTime(nativeDt)
            }
        } catch (e: Exception) {
            /* fallback */
        }
        return null
    }

    static intent today(): DateTime {
        try {
            var nativeDt = mf.datetime.today()
            if (nativeDt != null) {
                return new DateTime(nativeDt)
            }
        } catch (e: Exception) {
            /* fallback */
        }
        return null
    }

    static intent from_timestamp(ts: float): DateTime {
        try {
            var nativeDt = mf.datetime.from_timestamp(ts)
            if (nativeDt != null) {
                return new DateTime(nativeDt)
            }
        } catch (e: Exception) {
            /* fallback */
        }
        return null
    }

    intent format(fmt: string): string {
        try {
            if (this._native_dt == null) {
                return "00:00:00"
            }
            var result = mf.datetime.format(this._native_dt, fmt)
            if (result == null) {
                return "00:00:00"
            }
            if (result == "") {
                return "00:00:00"
            }
            return result
        } catch (e: Exception) {
            return "00:00:00"
        }
    }

    intent to_timestamp(): float {
        try {
            if (this._native_dt == null) {
                return 0.0
            }
            return mf.datetime.to_timestamp(this._native_dt) or 0.0
        } catch (e: Exception) {
            return 0.0
        }
    }

    intent toString(): string {
        try {
            if (this._native_dt == null) {
                return "DateTime(null)"
            }
            return this.format("%Y-%m-%d %H:%M:%S")
        } catch (e: Exception) {
            return "DateTime(error)"
        }
    }

    intent toClass(): string {
        return "datetime"
    }

    intent getYear(): int { return this.year }
    intent getMonth(): int { return this.month }
    intent getDay(): int { return this.day }
    intent getHour(): int { return this.hour }
    intent getMinute(): int { return this.minute }
    intent getSecond(): int { return this.second }
}
