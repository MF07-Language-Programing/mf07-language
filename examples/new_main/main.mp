# Minimal example to test class, intent and print

import new_main.person
from new_main.employee import Employee, Manager
from new_main.person import PessoaBase


class Pessoa {
    private var nome: string = "";
    intent constructor(nome: string) {
        this.nome = nome;
    }

    intent apresentar(): string {
        return this.nome
    }
}

# Top-level async helper
async intent runAsync(emp: Employee) {
    var r = await emp.fetchData()
    print("runAsync got:", r)
}

async intent main() {
    var emp = new Employee("Joao", "dev")
    print("role:", emp.getRole())
    print("nome:", emp.nome())

    # Calling async method from sync context -> should raise
    try {
        var maybe = emp.fetchData()
        print("unexpected success:", maybe)
    } catch (e: Exception) {
        print("Expected error when calling async from sync:", e)
        print(type(e))
    }

    # Correct usage: await the async function
    var result = await emp.fetchData()
    print("Awaited result:", result)

    # Inheritance
    var mgr = new Manager("Maria", "lead")
    print(mgr.manage())

    # Using interface from imported module
    var base = new PessoaBase("Anonimo")
    print("base name:", base.nome())

    # call top-level async helper
    await runAsync(emp)

    # kwargs capture demo: constructor and function that accept a trailing `kwargs` param
    var u = new User(pwd="1212", email="example@example.com", role="admin")
    try {
        print("user email:", u.email)
    } catch (e: Exception) {
        print("error accessing u.email:", e)
    }

    printKwargs(7, x = "vx", z = "vz")
}

# Class that demonstrates capturing extra named args in constructor
class User {
    private var email: string = null;

    intent constructor(pwd: string, kwargs) {
        this.pwd = pwd
        print("constructor: pwd=", pwd)
        print("constructor: kwargs=", kwargs)
        print("constructor: kwargs_type=", type(kwargs))
        print("constructor: kwargs.get('email')=", kwargs.get("email"))
        print("constructor: kwargs.get('role')=", kwargs.get("role"))
        this.email = kwargs.get("email")
    }
}

# Function that demonstrates capture of extra named args into `kwargs`
intent printKwargs(a: int, kwargs) {
    print("printKwargs: a=", a)
    print("printKwargs: kwargs.x=", kwargs.x)
    print("printKwargs: kwargs.get('z')=", kwargs.get("z"))
}

await main()
