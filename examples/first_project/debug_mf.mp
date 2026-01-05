print("DEBUG start")
try {
    print(mf)
    print(mf.fs)
    var r = mf.fs.write_text("tests/tmp_with/debug_direct.txt", "HELLO-DIRECT")
    print(f"write_text returned: {r}")
    var rr = mf.fs.read_text("tests/tmp_with/debug_direct.txt")
    print(f"read_text returned: {rr}")
} catch (e: Exception) {
    print("DEBUG exception: "+ e)
}
