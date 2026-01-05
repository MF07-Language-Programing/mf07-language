# Combined demo showing catches by type and category
try {
    __native__("open", "no_such_file_hopefully_missing.txt")
} catch (e: FileNotFoundError) {
    print("file caught by FileNotFoundError")
} catch (e: IO_ERROR) {
    print("file caught by IO_ERROR")
}

async intent do_both() {
    try {
        await might_timeout()
    } catch (x: TimeoutError) {
        print("timeout handled inside async")
    }
}

await do_both()