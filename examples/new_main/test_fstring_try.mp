async intent main() {
    try {
        var s = f"hello {missingVar}"
        print(s)
    } catch (e: Exception) {
        print("caught:", e)
    }
}

await main()
