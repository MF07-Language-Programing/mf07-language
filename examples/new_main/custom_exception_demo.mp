# Custom class-based exception demo

class MyError {
    intent constructor(msg: string) {
        this.msg = msg
    }
}

try {
    throw new MyError("boom")
} catch (e: MyError) {
    print("caught MyError via typed catch:", e.type, e.message)
} catch (e: Exception) {
    print("fallback caught:", e.type, e.message)
}
