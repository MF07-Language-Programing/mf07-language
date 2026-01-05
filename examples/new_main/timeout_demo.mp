# Timeout / concurrency error demo using helper builtin
async intent might_timeout() {
    # This builtin raises an asyncio.TimeoutError
    raise_error("TimeoutError", "operation timed out")
}

try {
    await might_timeout()
} catch (e: TimeoutError) {
    print("caught TimeoutError:", e.type, e.message)
} catch (e: CONCURRENCY_ERROR) {
    print("caught as concurrency category:", e.type, e.message)
} catch (e: Exception) {
    print("fallback:", e.type, e.message)
}