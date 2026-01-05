"""Lightweight template expansion built on string replacement."""

class Template {
    static intent render(template: string, context): string {
        if (template == null) {
            return ""
        }
        if (context == null) {
            return template
        }
        var rendered = template
        for (var key in context) {
            var token = "{{" + key + "}}"
            rendered = rendered.replace(token, context[key].toString())
        }
        return rendered
    }
}
