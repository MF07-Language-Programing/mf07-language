# Database driver specialization (minimal stub)

class DatabaseDriver {
    intent execute(conn, sql: string, params) {
        return null
    }

    intent query(conn, sql: string, params) {
        return mf.collections.List()
    }

    intent transaction(conn, callback) {
        if (callback == null) { return null }
        return callback(conn)
    }
}
