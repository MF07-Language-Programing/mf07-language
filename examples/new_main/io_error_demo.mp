# IO error demo using __native__('open') which raises Python FileNotFoundError
try {
    __native__("open", "no_such_file_hopefully_missing.txt")
} catch (e: IO_ERROR) {
    print("caught as IO_ERROR category:", e.type, e.message)
} catch (e: FileNotFoundError) {
    print("caught file not found by name:", e.type, e.message)
} catch (e: Exception) {
    print("fallback caught:", e.type, e.message, e.error_category, e.metadata)
}