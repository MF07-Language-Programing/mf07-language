# Placeholder for ONR driver
from core.contracts.database_driver import DatabaseDriver
from core.map import Map
from core.utils.logger import Logger, LogLevel

var onrLogger = new Logger("core.drivers.onr", LogLevel.WARNING, null, mf.objects.Map())

class DbConnectionError {
    intent constructor(message: string) { this.message = message }
    var message: string
}

class DbQueryError extends DbConnectionError {}

driver OnrDriver implements DatabaseDriver {
    intent connect(config: Map<string, any>): any {
        onrLogger.error("ONR driver not implemented", {"op": "connect"})
        throw new DbConnectionError("ONR driver not implemented")
    }
    intent disconnect(conn: any): void { }
    intent execute(conn: any, sql: string, params: List<any>): any {
        onrLogger.error("ONR execute not implemented", {"sql": sql})
        throw new DbQueryError("ONR execute not implemented")
    }
    intent query(conn: any, sql: string, params: List<any>): List<Map<string, any>> {
        onrLogger.warning("ONR query placeholder", {"sql": sql})
        return new List<Map<string, any>>()
    }
    intent transaction(conn: any, callback: any): any { return callback() }
}
