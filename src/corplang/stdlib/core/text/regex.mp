"""Simplified regex helpers."""

class Regex {
    static intent match(pattern: string, text: string): bool {
        try {
            return mf.regex.match(pattern, text)
        } catch (e: Exception) {
            return false
        }
    }

    static intent replace(pattern: string, repl: string, text: string): string {
        try {
            return mf.regex.replace(pattern, repl, text)
        } catch (e: Exception) {
            return text
        }
    }
}
