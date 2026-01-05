"""Test return and finally block execution."""

intent test_return_in_try(): bool {
    print("start test_return_in_try")
    try {
        print("in try block")
        return true
        print("this should NOT print")
    } finally {
        print("finally block executed")
    }
    print("this should NOT print either")
}

intent test_catch_and_finally(): bool {
    print("start test_catch_and_finally")
    var result = false
    try {
        print("in try block, throwing error")
        throw new RuntimeException("test error")
    } catch (e: Exception) {
        print(f"caught: {e}")
        result = true
        return result
        print("this should NOT print after return in catch")
    } finally {
        print("finally block executed after catch return")
    }
    print("this should NOT print either")
}

intent test() {
    try {
        return true
    } catch (e: Exception) {
        return false
    }
}

# Call tests
print("=== Test 1: Return in try ===")
var r1 = test_return_in_try()
print(f"test_return_in_try returned: {r1}")

print("\n=== Test 2: Return in catch ===")
var r2 = test_catch_and_finally()
print(f"test_catch_and_finally returned: {r2}")

print("\n=== Done ===")
var r = test()
print(r)