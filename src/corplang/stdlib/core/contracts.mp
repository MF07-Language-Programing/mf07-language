"""Contracts shim with minimal placeholder types to satisfy imports."""

class Driver {
	intent connect(config) { return null }
	intent disconnect(conn) { return null }
}

class DatabaseDriver extends Driver {
	intent execute(conn, sql: string, params) { return null }
	intent query(conn, sql: string, params) { return mf.collections.List() }
	intent transaction(conn, callback) { if (callback == null) { return null } return callback(conn) }
}

class Module { }
class ObjectContract { }
class Protocol { }
class TypeContract { }
