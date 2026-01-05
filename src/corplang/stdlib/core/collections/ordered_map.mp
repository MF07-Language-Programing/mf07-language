"""Ordered map preserving insertion order."""

class OrderedMap {
    private var data
    private var keys

    intent constructor(initial = null) {
        this.data = mf.objects.map()
        this.keys = mf.collections.List()
        if (initial != null) {
            for (var k in initial) {
                this.set(k, initial[k])
            }
        }
    }

    intent set(key, value) {
        if (!mf.objects.mapHas(this.data, key)) {
            this.keys.append(key)
        }
        this.data[key] = value
    }

    intent get(key, defaultValue = null) {
        if (mf.objects.mapHas(this.data, key)) {
            return this.data[key]
        }
        return defaultValue
    }

    intent items(): list {
        var result = []
        var i = 0
        while (i < len(this.keys)) {
            var key = this.keys[i]
            result.append([key, this.data[key]])
            i = i + 1
        }
        return result
    }
}
