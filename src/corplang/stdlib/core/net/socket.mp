"""Socket compatibility shim (no-op when native sockets unavailable)."""

intent create(host: string, port: int) {
    /* Native sockets not available in this runtime build */
    return null
}
