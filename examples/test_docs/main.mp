"""
Main module de demonstração para documentação
Este arquivo demonstra como o gerador de docs funciona
"""

interface IPessoa {
    intent getName(): string
    intent getAge(): int
}

class Pessoa implements IPessoa {
    """Classe que representa uma pessoa"""
    
    private var name: string
    private var age: int
    var email: string
    
    intent constructor(name: string, age: int, email: string = "") {
        """Cria uma nova instância de Pessoa
        
        Parâmetros:
        - name: Nome da pessoa
        - age: Idade da pessoa
        - email: Email da pessoa (opcional)
        """
        this.name = name
        this.age = age
        this.email = email
    }
    
    intent getName(): string {
        """Retorna o nome da pessoa"""
        return this.name
    }
    
    intent getAge(): int {
        """Retorna a idade da pessoa"""
        return this.age
    }
    
    intent apresentar(): string {
        """Gera uma apresentação da pessoa"""
        return f"Olá, sou {this.name} e tenho {this.age} anos"
    }
}

class Empresa {
    """Classe que representa uma empresa"""
    
    private var cnpj: string
    var nome: string
    var funcionarios: list = null
    
    intent constructor(nome: string, cnpj: string) {
        """Inicializa uma nova empresa
        
        Parâmetros:
        - nome: Nome da empresa
        - cnpj: CNPJ da empresa
        """
        this.nome = nome
        this.cnpj = cnpj
        this.funcionarios = []
    }
    
    intent adicionarFuncionario(pessoa: Pessoa): void {
        """Adiciona um funcionário à empresa"""
        this.funcionarios.append(pessoa)
    }
    
    intent totalFuncionarios(): int {
        """Retorna o número total de funcionários"""
        return len(this.funcionarios)
    }
}

intent saudacao(nome: string, pronome: string = "você"): string {
    """Função que gera uma saudação
    
    Parâmetros:
    - nome: Nome da pessoa a saudar
    - pronome: Pronome a usar (default: "você")
    
    Retorna:
    Uma string com a saudação
    """
    return f"Olá {nome}, como está {pronome}?"
}
