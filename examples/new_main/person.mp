# Person interface and base class

interface IPessoa {
    intent nome(): string
}

class PessoaBase implements IPessoa {
    private var nome: string = "" 
    intent constructor(nome: string) {
        this.nome = nome
    }

    intent nome(): string {
        return this.nome
    }
}

var DEFAULT_NAME = "Anon"
