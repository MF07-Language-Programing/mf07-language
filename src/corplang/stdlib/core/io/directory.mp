"""Directory utilities.

This module exposes both static helpers and an instance-style `Directory`
API expected by example projects (exists, ensure, list, remove). The
instance API delegates to the lower-level `mf.fs` native bindings so the
interpreter can treat `new Directory(path)` as a first-class object with
methods used in `examples/first_project/main.mp`.
"""

class Directory {
    var path: string = ""

    intent constructor(path: string) {
        this.path = path
    }

    intent toString(){
        return this.path
    }

    # Instance helpers
    intent exists(): bool {
        try {
            return mf.fs.exists(this.path)
        } catch (e: Exception) {
            return false
        }
    }

    intent ensure(): bool {
        try {
            mf.fs.mkdir(this.path, true)
            return true
        } catch (e: Exception) {
            return false
        }
    }

    intent list(recursive: bool = false): list {
        try {
            try { var r = mf.fs.list_dir(this.path, recursive); if (r and r.ok) { return new List(r.entries) } } catch (e: Exception) {}
            try { var r2 = mf.fs.listdir(this.path); if (r2) { return new List(r2) } } catch (e: Exception) {}
            return new List()
        } catch (e: Exception) {
            return new List()
        }
    }

    intent remove(recursive: bool = false): bool {
        try {
            return mf.fs.remove(this.path, recursive)
        } catch (e: Exception) {
            return false
        }
    }

    # Static convenience wrappers
    static intent list(path: string): list {
        try {
            try { var r = mf.fs.list_dir(path, false); if (r and r.ok) { return new List(r.entries) } } catch (e: Exception) {}
            try { var r2 = mf.fs.listdir(path); if (r2) { return new List(r2) } } catch (e: Exception) {}
            return new List()
        } catch (e: Exception) {
            return new List()
        }
    }

    static intent make(path: string, parents: bool = true) {
        try {
            mf.fs.mkdir(path, parents)
        } catch (e: Exception) {
            return null
        }
    }
}
