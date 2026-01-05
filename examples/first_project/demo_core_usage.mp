# Demo: usage of core modules and class features

# Uses List (core/list.mp), JSON (core/json.mp) and Object utilities

class Animal {
    var name: string = ""
    intent constructor(name) {
        this.name = name
    }
    intent speak() {
        print(this.name + " says: ...")
    }
}

class Dog extends Animal {
    static var species: string = "Canis familiaris"
    private var secret: string = "dog-secret"

    intent constructor(name) {
        this.name = name
    }

    intent speak() {
        print(this.name + " says: woof!")
    }

    intent getSecret() {
        return this.secret
    }

    intent print() {
        print("[Dog] " + this.name + " (species=" + Dog.species + ")")
    }
}

intent demo() {
    print("--- Demo core usage ---")
    var dogs = new List()
    dogs.append(new Dog(StringHelpers.toUpper("Buddy")))
    dogs.append(new Dog("Rex"))

    print("Dogs length:", dogs.length())
    print("Dogs as string:", dogs.toString())

    print("forEach via MF07 intent:")
    dogs.forEach(fn(d) { d.speak() })

    print("map to names:")
    var names = dogs.map(fn(d) { return d.name })
    print(names.toString())
    print("filter by name 'Rex':")

    print("JSON stringify names:", JSON.stringify(names))

    print("Object keys of first dog ---:", dogs[0].name)
    print("Object values of first dog:", Object.values(dogs[0]))
}
