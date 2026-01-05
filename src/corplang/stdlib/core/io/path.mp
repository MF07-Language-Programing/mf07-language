"""Path compatibility shim."""

var Path = path

intent join(a, b) { try { return path.join(a, b) } catch (e: Exception) { return a + "/" + b }
}

intent dirname(p) { try { return path.dirname(p) } catch (e: Exception) { return "" }
}

intent basename(p) { try { return path.basename(p) } catch (e: Exception) { return "" }
}
