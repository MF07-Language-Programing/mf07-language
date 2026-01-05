# Type demo: shows runtime type checks when interpreter.strict_types=True

# correct: int
var cols: int = 3
print("cols ok:", cols)

# incorrect: string into int - should raise when strict_types=True
try {
    var wrong: int = "three"
    print("unexpected, assigned wrong")
} catch (e: Exception) {
    print("caught type error (as expected):", e)
}

# union types
var x: int|float = 2
print("x as int ok:", x)
try {
    var y: int|float = "bad"
    print("unexpected y assigned")
} catch (e: Exception) {
    print("caught union type error:", e)
}

# class Name checking (requires instance)
from new_main.employee import Employee
var p: Employee = new Employee("Ana", "dev")
print("p class ok:", p.nome())
try {
    var pbad: Employee = "not an employee"
    print("unexpected pbad assigned")
} catch (e: Exception) {
    print("caught class type error:", e)
}
