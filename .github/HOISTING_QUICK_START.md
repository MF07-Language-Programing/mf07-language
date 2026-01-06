# Começando com Hoisting Semântico em Corplang

## 🚀 Como Usar

### Passo 1: Escrever Código Normal

Declare variáveis nos ramos `if/else` normalmente:

```corplang
intent processValue(flag: bool) {
    if (flag) {
        var output = "Opção A"
    } else {
        var output = "Opção B"
    }
    print(output)  // Agora funciona! ✅
}
```

### Passo 2: Compilar/Executar

Não é necessário fazer nada especial - o hoisting acontece automaticamente:

```bash
mf run programa.mp
# ou
mf compile programa.mp
```

### Passo 3: Desfrutar da Flexibilidade

Seu código agora é:
- ✅ Mais expressivo
- ✅ Mais limpo
- ✅ Sem boilerplate desnecessário

---

## 📝 Exemplos Práticos

### Exemplo 1: Formatação Condicional

**ANTES** (com workaround):
```corplang
intent format(verbose: bool) {
    var prefix: str
    if (verbose) {
        prefix = "[DEBUG] "
    } else {
        prefix = "[INFO] "
    }
    return prefix + "Message"
}
```

**DEPOIS** (mais natural):
```corplang
intent format(verbose: bool) {
    if (verbose) {
        var prefix = "[DEBUG] "
    } else {
        var prefix = "[INFO] "
    }
    return prefix + "Message"  // Hoisting automático! ✅
}
```

### Exemplo 2: Construção de Config

```corplang
intent loadConfig(env: str) {
    if (env == "production") {
        var config = {
            "timeout": 5000,
            "retries": 3
        }
    } else {
        var config = {
            "timeout": 1000,
            "retries": 1
        }
    }
    
    return config  // ✅ Ambos os ramos declaram config
}
```

### Exemplo 3: Processamento com Tipo Determinístico

```corplang
intent calculate(mode: int) {
    if (mode == 1) {
        var result: int = 100
    } else if (mode == 2) {
        var result: int = 200
    } else {
        var result: int = 300
    }
    
    return result * 2  // ✅ Tipo garantido em todos os ramos
}
```

---

## 🔍 Entendendo a Transformação

### O Que Acontece Internamente

```
Seu código (original):
┌─────────────────────────────────────────┐
│ if (cond) {                             │
│     var x = "A"                         │
│ } else {                                │
│     var x = "B"                         │
│ }                                       │
│ return x                                │
└─────────────────────────────────────────┘
         ↓ (durante parsing)
         
Código hoisted (interno):
┌─────────────────────────────────────────┐
│ var x = null              ← Elevado!    │
│ if (cond) {                             │
│     x = "A"               ← Assignment  │
│ } else {                                │
│     x = "B"               ← Assignment  │
│ }                                       │
│ return x                  ← Agora OK!   │
└─────────────────────────────────────────┘
```

### Quem Realiza Essa Transformação?

O módulo `scope_analyzer.py` detecta:
- ✅ Variável em todos os ramos
- ✅ Tipos compatíveis
- ✅ Sem uso antes da declaração

E então:
- ✅ Eleva a declaração
- ✅ Converte para assignments
- ✅ Valida a segurança

---

## ⚠️ O Que NÃO Fazer

### ❌ Não Misture Tipos

```corplang
// Isto NÃO vai funcionar
intent bad1(flag: bool) {
    if (flag) {
        var x: int = 42
    } else {
        var x: str = "text"  // ← Tipo diferente!
    }
    return x  // Qual é o tipo?
}
```

**Solução**: Use explicitamente a type union ou separate:

```corplang
// ✅ Correto: tipos compatíveis
intent good1(flag: bool) {
    if (flag) {
        var x: str = "42"
    } else {
        var x: str = "text"  // ← Mesmos tipos
    }
    return x
}
```

### ❌ Não Declare em Um Ramo Só

```corplang
// Isto NÃO vai funcionar
intent bad2(flag: bool) {
    if (flag) {
        var x = 1
    }
    // Falta no else
    return x  // x pode não estar definida!
}
```

**Solução**: Declare em ambos os ramos:

```corplang
// ✅ Correto: em ambos os ramos
intent good2(flag: bool) {
    if (flag) {
        var x = 1
    } else {
        var x = 2  // ← Agora sim!
    }
    return x
}
```

### ❌ Não Use Antes de Declarar

```corplang
// Isto NÃO vai funcionar
intent bad3(flag: bool) {
    if (flag) {
        print(x)       // ← Uso antes!
        var x = 1
    } else {
        var x = 2
    }
}
```

**Solução**: Declare antes de usar:

```corplang
// ✅ Correto: declarar antes de usar
intent good3(flag: bool) {
    if (flag) {
        var x = 1
        print(x)  // ← Depois de declarar
    } else {
        var x = 2
    }
}
```

---

## 🎯 Checklist: Seu Código Será Hoisted?

Responda SIM para todos:

- [ ] A variável é declarada em **TODOS** os ramos (if e else)?
- [ ] Os **tipos são iguais** em todos os ramos?
- [ ] **Nenhum uso antes** da primeira declaração?
- [ ] É um `if/else` estruturado (não nested fora de alcance)?

Se todos forem SIM → ✅ Seu código será hoisted automaticamente!

---

## 🚨 Mensagens de Erro

### Tipo Incompatível

```
ERROR: Type mismatch in hoisting attempt for 'x':
Expected: int, Found: str in else branch
Location: line 42, column 8
```

**Solução**: Harmonize os tipos entre os ramos.

### Variável Incompleta

```
ERROR: Variable 'x' not declared in all branches
Location: if statement at line 35
```

**Solução**: Adicione a declaração no ramo faltante.

### Referência Indefinida

```
ERROR: Reference to undefined variable 'x'
Location: line 50, column 12
```

**Motivo**: Hoisting não foi possível.
**Solução**: Declare explicitamente antes do if:

```corplang
var x: int
if (condition) {
    x = 1
} else {
    x = 2
}
```

---

## 📊 Comparação: Com vs Sem Hoisting

| Aspecto | Sem Hoisting | Com Hoisting |
|---------|-------------|-------------|
| **Linhas de código** | 8 | 6 |
| **Clareza** | Intermediária | Alta |
| **Type Safety** | Sim | Sim |
| **Performance** | Igual | Igual |
| **Natureza** | Explícita | Idiomática |

---

## 💡 Pro Tips

### Tip 1: Combine com Lambdas

```corplang
var getMode = fn(prod: bool) {
    if (prod) {
        var mode = "PRODUCTION"
    } else {
        var mode = "DEVELOPMENT"
    }
    return mode  // ✅ Hoisting funciona em lambdas também!
}
```

### Tip 2: Use em Métodos

```corplang
class Config {
    intent getTimeout(isFast: bool) {
        if (isFast) {
            var timeout: int = 1000
        } else {
            var timeout: int = 5000
        }
        return timeout  // ✅ Funciona em métodos!
    }
}
```

### Tip 3: Combine com Operadores

```corplang
intent buildPath(isWindows: bool) {
    if (isWindows) {
        var sep = "\\"
    } else {
        var sep = "/"
    }
    return "path" + sep + "to" + sep + "file"  // ✅ Funciona!
}
```

---

## 🤔 Perguntas Comuns

**P: Posso desabilitar hoisting?**
R: Não, mas pode usar declaração explícita (veja Tip 2 acima).

**P: Funciona em switch statements?**
R: Não, apenas if/else (switch tem semântica diferente).

**P: E em aninhados?**
R: Sim, cada nível aplica seu próprio hoisting:

```corplang
intent nested(a: bool, b: bool) {
    if (a) {
        var x = 1  // Hoisting ao if interno
        if (b) {
            var y = 2
        } else {
            var y = 3
        }
    }
    return x  // ❌ x não aqui (escopo do if)
}
```

---

## 📚 Próximas Etapas

1. **Ler o guia completo**: [HOISTING_USER_GUIDE.md](HOISTING_USER_GUIDE.md)
2. **Entender a arquitetura**: [SCOPE_HOISTING_SOLUTION.md](SCOPE_HOISTING_SOLUTION.md)
3. **Explorar o código**: `src/corplang/compiler/scope_analyzer.py`

---

## 🎉 Conclusão

Hoisting semântico em Corplang torna seu código:
- Mais **expressivo**
- Mais **natural**
- Mais **idiomático**

Sem sacrificar segurança ou performance!

**Feliz codificação em Corplang! 🚀**
