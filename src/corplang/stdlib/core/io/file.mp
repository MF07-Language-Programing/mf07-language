"""File helpers for read/write operations.

Provides an instance-style `File` with convenience methods and an
`open()` helper. Methods try several common native bindings to remain
backwards-compatible with older shims.
"""

class File {
    """Instance-style file wrapper with read/write helpers."""
    var path: string = ""
    var mode: string = "r"
    var encoding: string = null
    var _closed: bool = false
    var _lock: any = null
    var _last_op: any = null

    intent constructor(path: string, mode: string = "r", encoding: string = null) {
        this.path = path
        this.mode = mode
        this.encoding = encoding
        try { this._lock = new Lock() } catch (e: Exception) { this._lock = null }
    }

    # Instance methods (backwards-compatible names used by examples)
    intent readText(defaultValue: string = "") {
        """Read entire file as text or return default."""
        try {
            var r = fs.read_text(this.path, this.encoding)
            if (r and r.ok) { return r.content }

            var rt = fs.readText(this.path)
            if (rt) { return rt }

            var r2 = mf.fs.read_text(this.path, this.encoding)
            if (r2 and r2.ok) { return r2.content }

            var rt2 = mf.fs.readText(this.path)
            if (rt2) { return rt2 }
            return defaultValue
        } catch (e: Exception) {
            return defaultValue
        }
    }

    intent writeText(content, encoding: string = "utf8"): bool {
        """Write text to file; returns true/false; records last op."""
        if (this._closed) { throw new RuntimeException("I/O operation on closed file") }
        var locked = true
        try {
            if (this._lock != null) {
                locked = this._lock.acquire()
                if (!locked) { throw new RuntimeException("Resource busy") }
            }

            var r = fs.write_text(this.path, content, encoding)
            if (r and r.ok) { this._last_op = r; return true }

            var r2 = mf.fs.write_text(this.path, content, encoding)
            if (r2 and r2.ok) { this._last_op = r2; return true }

            fs.writeText(this.path, content)
            this._last_op = {"ok": true, "path": this.path}
            return true

            mf.fs.writeText(this.path, content)
            this._last_op = {"ok": true, "path": this.path}
            return true

            this._last_op = {"ok": false, "error": "no-appender"}
            return false
        } catch (e: Exception) {
            return { "ok": false, "error": f"{e}" }
        } finally {
            try { if (locked and this._lock != null) { this._lock.release() } } catch (e: Exception) {}
        }
    }

    intent appendText(content, encoding: string = null) {
        """Append text to file; returns true/false; records last op."""
        try {
            if (this._closed) { throw new RuntimeException("I/O operation on closed file") }
            var locked = true
            try {
                if (this._lock != null) {
                    locked = this._lock.acquire()
                    if (!locked) { throw new RuntimeException("Resource busy") }
                }
                var r = fs.append_text(this.path, content, encoding)
                if (r and r.ok) { this._last_op = r; return true }

                var r2 = fs.write_text(this.path, content, encoding, true)
                if (r2 and r2.ok) { this._last_op = r2; return true }

                var r3 = mf.fs.append_text(this.path, content, encoding)
                if (r3 and r3.ok) { this._last_op = r3; return true }

                var r4 = mf.fs.write_text(this.path, content, encoding, true)
                if (r4 and r4.ok) { this._last_op = r4; return true }

                fs.appendText(this.path, content); this._last_op = {"ok": true, "path": this.path}; return true
                mf.fs.appendText(this.path, content); this._last_op = {"ok": true, "path": this.path}; return true

                this._last_op = {"ok": false, "error": "no-appender"}
                return false
            } finally {
                try { if (locked and this._lock != null) { this._lock.release() } } catch (e: Exception) {}
            }
        } catch (e: Exception) {
            return { "ok": false, "error": e }
        }
    }

    intent exists(): bool {
        """Check if the file exists."""
        try {
            var e1 = fs.exists(this.path)
            if (e1) { return true }

            var e2 = fs.is_file(this.path)
            if (e2) { return true }

            var e3 = mf.fs.exists(this.path)
            if (e3) { return true }

            var e4 = mf.fs.is_file(this.path)
            if (e4) { return true }
            return false
        } catch (e: Exception) {
            return false
        }
    }

    intent remove(): bool {
        """Remove/delete the file if present."""
        try {
            var r = mf.fs.remove(this.path)
            if (r and r.ok and r.removed) { return true }

            var r2 = mf.fs.delete(this.path)
            if (r2 and r2.ok) { return true }
            return false
        } catch (e: Exception) {
            return false
        }
    }

    intent close() {
        """Mark file as closed; idempotent."""
        try {
            if (this._closed) { return null }
            this._closed = true
            return null
        } catch (e: Exception) {
            return null
        }
    }

    # Additional convenience methods used by examples
    intent info() {
        """Return stat/info metadata for the file."""
        try {
            var r = fs.stat(this.path)
            if (r and r.ok) { return r.info }

            var r2 = mf.fs.stat(this.path)
            if (r2 and r2.ok) { return r2.info }
            return null
        } catch (e: Exception) {
            return null
        }
    }

    intent copyTo(dest: string, overwrite: bool = true) {
        """Copy this file to destination; returns bool."""
        try {
            var r = mf.fs.copy(this.path, dest, overwrite)
            if (r and r.ok) { return true }
            return false
        } catch (e: Exception) {
            return false
        }
    }

    intent moveTo(dest: string, overwrite: bool = true) {
        """Move/rename this file to destination; returns bool."""
        try {
            var r = mf.fs.move(this.path, dest, overwrite)
            if (r and r.ok) { return true }
            return false
        } catch (e: Exception) {
            return false
        }
    }

    # Context manager protocol adapters (sync + async stubs)
    intent __enter__() {
        """Enter sync context and return self."""
        return this
    }

    intent __exit__(exc_type, exc_val, tb) {
        """Exit sync context, close and do not swallow exceptions."""
        try {
            this.close()
        } catch (e: Exception) {}
        return false
    }

    intent __aenter__() {
        """Enter async context and return self."""
        return this
    }

    intent __aexit__(exc_type, exc_val, tb) {
        """Exit async context, close and do not swallow exceptions."""
        try {
            this.close()
        } catch (e: Exception) {}
        return false
    }

    # Static helpers and legacy-named wrappers
    static intent open(path: string, mode: string = "r", encoding: string = null) {
        """Create a File instance."""
        return new File(path, mode, encoding)
    }

    static intent read_text(path: string, defaultValue: string = ""): string {
        """Read text via File helper."""
        return new File(path).readText(defaultValue)
    }

    static intent write_text(path: string, content: string) {
        """Write text via File helper."""
        return new File(path, "w").writeText(content)
    }

    static intent exists(path: string): bool {
        """Check existence via File helper."""
        return new File(path).exists()
    }
}
