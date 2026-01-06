# Guia de Uso: Hoisting Semântico em Corplang

## 🎯 O que é Hoisting Semântico?

Hoisting semântico é um mecanismo que **eleva automaticamente** variáveis declaradas em ramos mutuamente exclusivos para o escopo do bloco pai (função/método).

## ✅ Casos que FUNCIONAM com Hoisting

### 1. String/Valor Progressivo

```corplang
intent buildGreeting(formal: bool) {
    if (formal) {
        var greeting = "Prezado"
    } else {
        var greeting = "Oi"
    }
    return greeting + " usuário!"  // ✅ Funciona
}
```

**Por quê**: A variável é declarada em **ambos** os ramos com o **mesmo tipo**.

### 2. Construção Condicional

```corplang
intent formatOutput(debug: bool) {
    if (debug) {
        var output = "[DEBUG] "
    } else {
        var output = "[INFO] "
    }
    var final = output + "Mensagem"  // ✅ Funciona
    return final
}
```

### 3. Processamento com Tipos Determinísticos

```corplang
intent calculate(mode: int) {
    if (mode == 1) {
        var result: int = 10
    } else {
        var result: int = 20
    }
    return result * 2  // ✅ Funciona (ambos são int)
}
```

### 4. Múltiplas Variáveis em Ramos

```corplang
intent processData(isVerbose: bool) {
    if (isVerbose) {
        var prefix = "LOG: "
        var level = "DEBUG"
    } else {
        var prefix = ">> "
        var level = "INFO"
    }
    return prefix + level  // ✅ Ambas as variáveis são hoisted
}
```

## ❌ Casos que NÃO funcionam (e por quê)

### 1. Tipos Incompatíveis

```corplang
intent getValue(option: bool) {
    if (option) {
        var value: int = 42      // int
    } else {
        var value: str = "Hello"  // string ← Incompatível!
    }
    print(value)  // ❌ Erro: tipos não coincidem
}
```

**Motivo**: Type safety - não dá para saber qual tipo `value` teria.

### 2. Declaração em Apenas Um Ramo

```corplang
intent conditional(c: bool) {
    if (c) {
        var x = 1
    }
    // Falta 'else' ou declaração no else
    print(x)  // ❌ Erro: x pode não estar definida
}
```

**Motivo**: A variável pode não ser inicializada se a condição for falsa.

### 3. Uso Antes da Declaração

```corplang
intent invalid(c: bool) {
    if (c) {
        print(x)       // ❌ Uso antes de declarar!
        var x = 1
    } else {
        var x = 2
    }
}
```

**Motivo**: Viola a regra de uso após inicialização.

### 4. Bloco Condicional Aninhado

```corplang
intent nested(c1: bool, c2: bool) {
    if (c1) {
        if (c2) {
            var x = 1
        } else {
            var x = 2  // Hoisting aqui é ao if/else interno
        }
    }
    print(x)  // ❌ Erro: x não visível neste escopo
}
```

**Motivo**: Hoisting é local ao bloco mais próximo, não "pula" para o exterior.

## 🔄 Transformação que Ocorre

### Antes (seu código)

```corplang
intent example(flag: bool) {
    if (flag) {
        var message = "Yes"
    } else {
        var message = "No"
    }
    return message
}
```

### Depois (internamente após parse)

```corplang
intent example(flag: bool) {
    var message = null           // ← Hoisted!
    if (flag) {
        message = "Yes"          // ← Converted to assignment
    } else {
        message = "No"           // ← Converted to assignment
    }
    return message
}
```

**Nota**: Você **não vê** essa transformação - acontece automaticamente durante parsing.

## 📝 Boas Práticas

### ✅ DO: Padrões Recomendados

```corplang
// Bom: Hoisting automático
intent buildConfig(env: str) {
    if (env == "prod") {
        var config = getProductionConfig()
    } else {
        var config = getDevelopmentConfig()
    }
    applyConfig(config)  // Limpo e seguro
}
```

```corplang
// Bom: Explícito quando complexo
intent complexLogic(a: int, b: int) {
    var result: int       // Declare antecipadamente se quiser ser explícito
    if (a > b) {
        result = a
    } else {
        result = b
    }
    return result
}
```

### ❌ DON'T: Padrões a Evitar

```corplang
// Ruim: Use completo sem declaração
intent problematic(c: bool) {
    if (c) {
        var x = 1
    }
    // x pode não estar definida!
    return x
}
```

```corplang
// Ruim: Tipos mistos em ramos
intent confused(flag: bool) {
    if (flag) {
        var value: int = 42
    } else {
        var value: str = "text"  // ← Inconsistente
    }
    return value  // Qual é o tipo?
}
```

```corplang
// Ruim: Lógica que invalida hoisting
intent impossible(c: bool) {
    if (c) {
        var x = 1
    } else {
        var y = 2  // ← Variável diferente!
    }
    return x + y  // ❌ y nem sempre definida
}
```

## 🔍 Como Saber se Hoisting foi Aplicado

### Método 1: Olhar para Erros

Se você receberia `REFERENCE_ERROR` **antes** de aplicar a solução, mas o código agora funciona → hoisting foi aplicado!

### Método 2: Debugar

Ative o modo verbose do compilador para ver transformações:

```bash
mf compile --verbose programa.mp
```

### Método 3: Entender a Regra

**Hoisting é aplicado se e somente se**:
- ✅ Variável é declarada em **todos** os ramos de if/else
- ✅ Os ramos são **mutuamente exclusivos** (estruturado if/else)
- ✅ Os **tipos coincidem** em todos os ramos
- ✅ Não há **uso antes** da declaração

## 🚀 Migrando Código Legado

Se você tem código que **precisa de hoisting**, aqui estão as opções:

### Opção 1: Deixar o Hoisting Automático (Recomendado)

```corplang
// Seu código atual que funciona:
intent oldStyle(c: bool) {
    var value: int
    if (c) {
        value = 1
    } else {
        value = 2
    }
    return value
}

// Agora você PODE escrever assim (hoisting automático):
intent newStyle(c: bool) {
    if (c) {
        var value = 1
    } else {
        var value = 2
    }
    return value  // ✅ Funciona!
}
```

### Opção 2: Ser Explícito (Sempre Válido)

```corplang
intent explicit(c: bool) {
    var value: int
    if (c) {
        value = 1
    } else {
        value = 2
    }
    return value
}
```

Ambos são agora equivalentes!

## ❓ FAQ

### P: Hoisting funciona em loops?

R: Não, por enquanto apenas em `if/else`. Loops têm semântica mais complexa.

### P: E se eu quiser desabilitar hoisting?

R: Não é possível desabilitar, mas você pode fazer declarações explícitas (veja Opção 2 acima).

### P: Afeta performance?

R: Não! Hoisting acontece no parsing (tempo de compilação), zero overhead em runtime.

### P: Funciona em métodos de classe?

R: Sim! Hoisting funciona em qualquer função/método dentro da linguagem.

### P: Posso usar com tipos customizados?

R: Sim, desde que o tipo seja **exatamente** o mesmo em ambos os ramos:

```corplang
class Person {
    var name: str
}

intent getPerson(flag: bool) {
    if (flag) {
        var p: Person = new Person()
    } else {
        var p: Person = new Person()  // ✅ Mesmo tipo
    }
    return p
}
```

## 📚 Documentação Relacionada

- **Technical Deep Dive**: `.github/SCOPE_HOISTING_SOLUTION.md`
- **Implementation Summary**: `.github/HOISTING_IMPLEMENTATION_SUMMARY.md`
- **Source Code**: `src/corplang/compiler/scope_analyzer.py`

## 💡 Resumo

Hoisting semântico em Corplang:
- ✅ Faz seu código mais natural e expressivo
- ✅ Mantém segurança de tipos
- ✅ Zero custo de performance
- ✅ Transparente e automático
- ✅ Rejusta com erro claro se algo não se encaixa

**Use-o para escrever código mais idiomático em Corplang! 🚀**
