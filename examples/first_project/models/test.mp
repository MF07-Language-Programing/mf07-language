class Person {
    var name: string = ""
    var age: int = 0

    intent constructor(name: string, age: int) {
        console.debug(f"Creating person: {name}, age {age}")
        this.name = name
        this.age = age
    }

    intent close(){
        console.debug(f"Closing person: {this.name}")
    }

    intent getName() {
        return this.name
    }

    intent greet() {
        console.debug(f"Hello, {this.name}, age {this.age}")
    }

    intent toString(){
        return f"Person<name={this.getName()} | age={this.age}>"
    }
}

var p = new Person("Alice", 30)
p.greet()

console.debug(p)
