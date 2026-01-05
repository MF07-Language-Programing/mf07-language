# Generic driver contract for pluggable subsystems

interface Driver {
    intent connect(config: Map<string, any>): any
    intent disconnect(conn: any): void
}
