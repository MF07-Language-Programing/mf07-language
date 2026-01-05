# Stack trace demo: nested calls
fn c() {
    throw "deep failure"
}
fn b() {
    return c()
}
fn a() {
    return b()
}

try {
    a()
} catch (e: Exception) {
    e.printStackTrace()
}
