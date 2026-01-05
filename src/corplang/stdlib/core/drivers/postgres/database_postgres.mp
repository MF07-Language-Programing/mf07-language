# Placeholder for Postgres driver
from core.contracts.database_driver import DatabaseDriver
from core.map import Map
from core.utils.logger import Logger, LogLevel

var pgLogger = new Logger("core.drivers.postgres", LogLevel.WARNING, null, mf.objects.Map())

class DbConnectionError {
    intent constructor(message: string) { this.message = message }
    var message: string
}

class DbQueryError extends DbConnectionError {}

driver PostgresDriver implements DatabaseDriver {
    intent connect(config: Map<string, any>): any {
        pgLogger.error("Postgres driver not implemented", {"op": "connect"})
        throw new DbConnectionError("Postgres driver not implemented")
    }
    intent disconnect(conn: any): void { }
    intent execute(conn: any, sql: string, params: List<any>): any {
        pgLogger.error("Postgres execute not implemented", {"sql": sql})
        throw new DbQueryError("Postgres execute not implemented")
    }
    intent query(conn: any, sql: string, params: List<any>): List<Map<string, any>> {
        pgLogger.warning("Postgres query placeholder", {"sql": sql})
        return new List<Map<string, any>>()
    }
    intent transaction(conn: any, callback: any): any { return callback() }
}
