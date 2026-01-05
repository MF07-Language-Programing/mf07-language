"""Filesystem compatibility shim for legacy imports."""

# Forward to native fs/path where available.
var fs = fs
var path = path

intent readText(filePath: string): string {
    try { return fs.readText(filePath) } catch (e: Exception) { return "" }
}

# Convenience helpers to match common APIs used in examples
intent open(path: string, mode: string = "r", encoding: string = null) {
    try { return File.open(path, mode, encoding) } catch (e: Exception) { return null }
}

intent open_async(path: string, mode: string = "r", encoding: string = null) {
    # Placeholder: returns the same object; proper async adapter implemented in runtime/native layer
    try { return File.open(path, mode, encoding) } catch (e: Exception) { return null }
}

intent writeText(filePath: string, data): bool {
    try { fs.writeText(filePath, data); return true } catch (e: Exception) { return false }
}

# Compatibility class exposing `FileSystem` used by examples/tests
class FileSystem {
    static intent readText(p, defaultValue: string = "") {
        try {
            try { var r = mf.fs.read_text(p); if (r and r.ok) { return r.content } } catch (e: Exception) {}
            try { return fs.readText(p) } catch (e: Exception) {}
            return defaultValue
        } catch (e: Exception) {
            return defaultValue
        }
    }

    static intent writeText(p, data) {
        try {
            try { var r = mf.fs.write_text(p, data); return r and r.ok } catch (e: Exception) {}
            try { return writeText(p, data) } catch (e: Exception) {}
            return false
        } catch (e: Exception) {
            return false
        }
    }

    static intent readJSON(p, defaultValue = null) {
        try { var r = mf.fs.read_json(p); if (r and r.ok) { return r.data } } catch (e: Exception) {}
        return defaultValue
    }

    static intent writeJSON(p, data) {
        try { var r = mf.fs.write_json(p, data); return r and r.ok } catch (e: Exception) { return false }
    }

    static intent exists(p) {
        try { return mf.fs.exists(p) } catch (e: Exception) { return false }
    }

    static intent listDir(p, recursive: bool = false) {
        try { var r = mf.fs.list_dir(p, recursive); if (r and r.ok) { return new List(r.entries) } } catch (e: Exception) {}
        return new List()
    }

    static intent glob(p, pattern) {
        try { var r = mf.fs.glob(p, pattern); if (r and r.ok) { return new List(r.matches) } } catch (e: Exception) {}
        return new List()
    }

    static intent walk(p) {
        try { var r = mf.fs.walk(p); if (r and r.ok) { return new List(r.entries) } } catch (e: Exception) {}
        return new List()
    }

    static intent remove(p, recursive: bool = false) {
        try { var r = mf.fs.remove(p, recursive); return r and r.ok and (r.removed or true) } catch (e: Exception) { return false }
    }

    static intent stat(p) {
        try { var r = mf.fs.stat(p); if (r and r.ok) { return r.info } } catch (e: Exception) {}
        return null
    }
}
