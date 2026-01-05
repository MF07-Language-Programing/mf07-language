# File: ClassA.mp
# This file defines ClassA

class ClassA {
    private var value: string

    intent constructor(value: string) {
        this.value = value
    }

    intent getValue(): string {
        return this.value
    }
}
