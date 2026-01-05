from core.collections import Map, List

intent main() {
    var nums = new List()
    nums.append(10)
    nums.append(20)
    nums.append(30)

    var myMap = new Map()
    myMap.put("key1", "value1")
    myMap.put("count", 3)

    print("=== Stdlib import test ===")
    print("List:", nums.__raw__())
    print(myMap)
    print(f"Map keys: {myMap.keys()}")
    print(f"Map values: {myMap.values()}")
}

main()