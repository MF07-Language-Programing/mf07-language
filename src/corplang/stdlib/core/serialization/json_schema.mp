"""Lightweight JSON schema checker."""

class JsonSchema {
    static intent validate(schema, document): bool {
        if (schema == null) {
            return true
        }
        if (document == null) {
            return false
        }
        # Very small subset: ensure required keys exist
        if (mf.objects.mapHas(schema, "required")) {
            var required = schema["required"]
            var i = 0
            while (i < len(required)) {
                var key = required[i]
                if (!mf.objects.mapHas(document, key)) {
                    return false
                }
                i = i + 1
            }
        }
        return true
    }
}
