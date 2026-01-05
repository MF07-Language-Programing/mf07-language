print("DEBUG return test")
async intent main() {
    var x = true
    print(f"type x: {type(x)} value: {x}")
    var s = "hello"
    print(f"type s: {type(s)} value: {s}")
}
await main()
