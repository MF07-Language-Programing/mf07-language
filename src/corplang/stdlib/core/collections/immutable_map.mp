"""Immutable map with copy-on-write semantics."""

class ImmutableMap {
    private var data

    intent constructor(initial = null) {
        if (initial == null) {
            this.data = mf.objects.map()
        } else {
            this.data = initial
        }
    }

    intent set(key, value): ImmutableMap {
        var clone = mf.objects.map()
        for (var k in this.data) {
            clone[k] = this.data[k]
        }
        clone[key] = value
        return new ImmutableMap(clone)
    }

    intent get(key, defaultValue = null) {
        if (mf.objects.mapHas(this.data, key)) {
            return this.data[key]
        }
        return defaultValue
    }

    intent toMap() {
        return this.data
    }
}
