# Try/Catch/Finally demo

try {
    throw "simple error"
} catch (e: Exception) {
    print("caught generic:", e.type, e.message)
} finally {
    print("finally ran")
}

# Typed catch demo
try {
    throw "type error occurred"
} catch (e: TypeError) {
    print("caught TypeError:", e.type, e.message)
} catch (e: Exception) {
    print("caught fallback:", e.type, e.message)
}

# Rethrow demo
try {
    try {
        throw "inner"
    } catch (inner: Exception) {
        print("inner caught, rethrowing")
        throw inner
    }
} catch (outer: Exception) {
    print("outer caught:", outer.type, outer.message)
} finally {
    print("outer finally")
}