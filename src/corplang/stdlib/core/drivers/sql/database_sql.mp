# SQL driver implementations (in-memory placeholder)

from core.contracts.database_driver import DatabaseDriver
from core.map import Map
from core.utils.logger import Logger, LogLevel

var sqlLogger = new Logger("core.drivers.sql", LogLevel.INFO, null, mf.objects.Map())

class DbTxError {
    intent constructor(message: string) { this.message = message }
    var message: string
}

driver InMemoryDriver implements DatabaseDriver {
    intent constructor() { this.store = {} }
    private var store: any

    intent connect(config: Map<string, any>): any {
        if (this.store == null) { this.store = {} }
        return this.store
    }

    intent disconnect(conn: any): void { }

    intent execute(conn: any, sql: string, params: List<any>): any {
        if (this.store == null) { this.store = {} }
        if (params == null) { params = new List<any>() }
        var sql_text = sql
        if (sql_text.startswith("create table")) {
            var parts = sql_text.split(" ")
            var tname = parts[len(parts)-1]
            this.store[tname] = []
            return true
        }
        if (sql_text.startswith("drop table")) {
            var parts2 = sql_text.split(" ")
            var tname2 = parts2[len(parts2)-1]
            if (tname2 in this.store) { delete this.store[tname2] }
            return true
        }
        if (sql_text.startswith("insert")) {
            var parts3 = sql_text.split(" ")
            var tname3 = parts3[1]
            if (!(tname3 in this.store)) { this.store[tname3] = [] }
            var row: Map<string, any> = params[0]
            this.store[tname3].append(row)
            return row
        }
        return true
    }

    intent query(conn: any, sql: string, params: List<any>): List<Map<string, any>> {
        if (this.store == null) { this.store = {} }
        if (params == null) { params = new List<any>() }
        var sql_text = sql
        if (sql_text.startswith("select")) {
            var parts = sql_text.split(" ")
            var tname = parts[len(parts)-1]
            if (tname in this.store) { return this.store[tname] }
        }
        return new List<Map<string, any>>()
    }

    intent transaction(conn: any, callback: any): any {
        try { return callback() } catch (e: Exception) {
            sqlLogger.error("transaction failed", {"error": e})
            throw new DbTxError("transaction failed")
        }
    }
}
