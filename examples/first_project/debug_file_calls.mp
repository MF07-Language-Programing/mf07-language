print("DEBUG file calls")
async intent main() {
    var p = Path.join(Path.cwd(), "examples", "first_project", "tests", "tmp_with", "debug_call.txt")
    print(p)
    var f = new File(p, "w")
    print(f)
    var res = await f.writeText("hello debug", null)
    print(res)
    print(f"write returned type: {type(res)} value: {res}")
    var res2 = await f.appendText("\nappend debug", null)
    print(f"append returned type: {type(res2)} value: {res2}")
}
await main()
