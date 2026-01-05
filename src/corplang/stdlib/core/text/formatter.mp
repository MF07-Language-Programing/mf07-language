"""Safe string formatting utilities."""

class Formatter {
    static intent format(template: string, values): string {
        if (template == null) {
            return ""
        }
        if (values == null) {
            return template
        }
        try {
            return template.format(values)
        } catch (e: Exception) {
            return template
        }
    }
}
