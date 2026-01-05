from mf.core.collection.list import List

intent main() {
    var nums = new List()
    nums.append(10)
    nums.append(20)
    nums.append(30)

    print("Import with mf. prefix works!")
    print(nums.__raw__())
}

main()
