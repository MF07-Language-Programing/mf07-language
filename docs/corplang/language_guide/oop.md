# Orientação a Objetos na Corplang

A Corplang oferece um sistema de classes completo, focado em extensibilidade e contratos claros, essencial para grandes projetos corporativos.

## Classes e Drivers

Uma classe é declarada com `class`. Se a classe interage diretamente com recursos de baixo nível ou hardware/IO, ela pode ser declarada como `driver`.

```corplang
class Pessoa {
    var nome: string
    private var idade: int

    intent constructor(nome: string, idade: int) {
        this.nome = nome
        this.idade = idade
    }

    intent saudar() {
        print("Olá, eu sou {this.nome}");
    }
}
```

### Modificadores de Acesso
*   `public` (padrão): Acessível de qualquer lugar.
*   `private`: Acessível apenas dentro da própria classe.
*   `protected`: Acessível na classe e em suas subclasses.

---

## Herança e Interfaces

A Corplang suporta herança simples e múltiplas interfaces.

### Extensão (extends)
```corplang
class Funcionario extends Pessoa {
    var cargo: string
    
    intent constructor(nome: string, idade: int, cargo: string) {
        super(nome, idade)
        this.cargo = cargo
    }
}
```

### Interfaces e Contratos (implements)
Interfaces definem apenas as assinaturas, enquanto contratos podem incluir regras de validação adicionais.

```corplang
interface IAutenticavel {
    intent login(senha: string): bool
}

class Usuario implements IAutenticavel {
    intent login(senha: string): bool {
        // Lógica de login
        return true
    }
}
```

---

## Genéricos

O suporte a genéricos permite criar componentes reutilizáveis que mantêm a segurança de tipos.

```corplang
class Caixa<T> {
    private var item: T
    
    intent set(item: T) {
        this.item = item
    }
    
    intent get(): T {
        return this.item
    }
}

var caixaDeTexto = new Caixa<string>();
caixaDeTexto.set("Segredo");
```

---

## Métodos Estáticos
Métodos marcados com `static` pertencem à classe e não a uma instância específica, sendo chamados diretamente pelo nome da classe.

```corplang
class Utils {
    static intent versao() {
        return "1.0.0";
    }
}
```
