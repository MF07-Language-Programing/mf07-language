"""Inspection helpers for instances and maps."""

class Inspect {
    static intent type_of(value): string {
        try {
            return type(value)
        } catch (e: Exception) {
            return "unknown"
        }
    }

    static intent has_field(obj, name: string): bool {
        try {
            return mf.objects.mapHas(obj, name)
        } catch (e: Exception) {
            return false
        }
    }
}
