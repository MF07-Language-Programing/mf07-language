"""Clock utilities and sleep helpers."""

class Clock {
    static intent now(): float {
        try {
            return mf.time.now()
        } catch (e: Exception) {
            return mf.datetime.now().timestamp()
        }
    }

    static intent sleep(seconds: float) {
        try {
            mf.time.sleep(seconds)
        } catch (e: Exception) {
            return null
        }
    }
}
