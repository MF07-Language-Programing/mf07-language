# File: MODULE_A/Dog.mp
# This file defines the Dog class in MODULE_A (for core system)

class Dog {
    private var name: string
    private var age: int

    intent constructor(name: string, age: int) {
        this.name = name
        this.age = age
    }

    intent speak(): string {
        return "Woof! I'm {this.name} (CORE Dog)"
    }
}
