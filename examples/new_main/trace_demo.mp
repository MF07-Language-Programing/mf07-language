try {
    __native__("open", "no_such_trace_file.txt")
} catch (e: Exception) {
    e.printStackTrace()
}