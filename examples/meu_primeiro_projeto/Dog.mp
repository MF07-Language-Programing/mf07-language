# File: Dog.mp
# This file defines the Dog class

class Dog {
    private var name: string
    private var age: int

    intent constructor(name: string, age: int) {
        this.name = name
        this.age = age
    }

    intent speak(): string {
        return "Woof! I'm {this.name}"
    }
}
