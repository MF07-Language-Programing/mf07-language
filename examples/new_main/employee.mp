from new_main.person import PessoaBase

class Employee extends PessoaBase {
    private var role: string = ""
    intent constructor(nome: string, role: string = "dev") {
        super(nome)
        this.role = role
    }

    intent getRole(): string {
        return this.role
    }

    async intent fetchData(): string {
        # simulate I/O
        waitSeconds(1)
        return f"fetched for {this.nome()}"
    }
}

class Manager extends Employee {
    intent manage(): string {
        return f"managing {this.getRole()}"
    }
}
