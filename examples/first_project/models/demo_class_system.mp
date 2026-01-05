# Demo: class system features

interface Printable {
    intent print()
}

abstract class Animal implements Printable {
    var name: string = ""
    private var secret: string = "top-secret"

    intent constructor(name: string) {
        this.name = name
    }

    intent getSecret() {
        return this.secret
    }

    # abstract method (empty body to signal abstractness)
    abstract intent speak() {}

    intent __repr__() {
        return "<Animal(name={this.name}, secret={this.secret})>"
    }
}

class Dog extends Animal {
    static var species: string = "Canis familiaris"

    intent constructor(name: string) {
        # call parent constructor by directly setting fields (no super yet)
        this.name = name
    }

    intent speak() {
        console.debug(this.name + " says: woof!")
    }

    intent print() {
        console.debug("[Dog] " + this.name + " (species=" + Dog.species + ")")
    }
}

class Cat extends Animal {
    intent constructor(name: string) {
        this.name = name
    }

    intent speak() {
        console.debug(this.name + " says: meow!")
    }
}

intent demoList() {
    console.debug("Demonstrating class system features")
    console.debug("Creating animals")
    var animals = []
    var d = new Dog("Rex")
    var c = new Cat("Mittens")
    animals.append(d)
    animals.append(c)

    console.debug("--- Demonstrating polymorphism and lists ---")
    var i = 0
    while (i < len(animals)) {
        print("----"*5,i ,"----"*5)
        var a = animals[i]
        a.speak()
        console.debug("Representation={a.__repr__()}")
        i = i + 1
        print("[","===="*5,i ,"===="*5, "]")
    }

    console.debug("Dog secret via method: {d.getSecret()}")
    console.debug("Dog secret via field: {d.secret}")
}

demoList()

# --- super() demonstration ---
class Base {
    var x: int = 0
    intent constructor(x: int) {
        this.x = x
        console.debug("Base constructor called with x= {x}")
    }
    intent getX() { return this.x }
}

class Derived extends Base {
    var y: int = 0
    intent constructor(x: int, y: int) {
        super(x)
        this.y = y
        console.debug(f"Derived constructor called with y= {y}")
    }
    intent getY() { return this.y }
    intent showBoth() {
        console.debug("[Derived] x= {this.getX()} y= {this.getY()}")
    }
}

model operation modelName
dataset operation datasetName

var d = new Derived(5, 9)
d.showBoth()
