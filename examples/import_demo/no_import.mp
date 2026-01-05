intent main() {
    var total: int = 0
    var i: int = 0

    while (i < 5) {
        total = total + i
        i = i + 1
    }

    print("sum=")
    print(total)
}

main()