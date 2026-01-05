print("DEBUG file sync call")
intent main() {
    var p = Path.join(Path.cwd(), "examples", "first_project", "tests", "tmp_with", "debug_call_sync.txt")
    var f = new File(p, "w")
    var res = f.writeText("hello sync", null)
    print(f"write sync returned type: {type(res)} value: {res}")
}
main()
