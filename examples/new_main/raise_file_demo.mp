# Directly raising a FileNotFoundError using raise_error builtin
try {
    raise_error("FileNotFoundError", "boom")
} catch (e: FileNotFoundError) {
    print("caught by name:", e.type, e.error_category)
} catch (e: IO_ERROR) {
    print("caught by category:", e.type, e.error_category)
} catch (e: Exception) {
    print("fallback:", e.type, e.error_category)
}