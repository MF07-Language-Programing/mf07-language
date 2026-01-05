# IA e Agentes (Runtime)

A Corplang não é apenas uma linguagem de programação tradicional; ela é uma linguagem orientada a Agentes de IA. O suporte para inteligência artificial é nativo e profundamente integrado ao runtime da Meta-Framework (`mf`).

## O Conceito de Agente

Um `agent` na Corplang é uma entidade autônoma que combina:
1.  **Inteligência**: Configuração do modelo de linguagem e provedor.
2.  **Contexto**: Regras de segurança e ferramentas (intents/classes) permitidas.
3.  **Execução**: Parâmetros de performance e caching.
4.  **Interface**: Endpoints de serviço e autenticação.

## Declaração de Agente

A sintaxe de declaração é declarativa e organizada em blocos:

```corplang
agent AssistenteFinanceiro {
    intelligence {
        provider "openai"
        capability "analysis"
    }
    
    context {
        allow intent calculate_tax
        allow class Transaction
    }
    
    execution {
        async true
    }
    
    authentication {
        token { value "segredo" }
        cors { enabled true }
    }
}
```

## Comandos de Agente

Além da declaração, a Corplang oferece comandos diretos para o ciclo de vida dos agentes:

### `agent train`
Inicia o processo de treinamento ou fine-tuning de um agente com dados específicos.
```corplang
agent train AssistenteFinanceiro with { "source": "relatorios.csv" };
```

### `serve`
Expõe um agente como um serviço de rede (ex: HTTP).
```corplang
serve http port 8080 name "api-financeira" using AssistenteFinanceiro;
```

### `loop`
Cria um loop de interação contínua, útil para assistentes de terminal.
```corplang
loop stdin using AssistenteFinanceiro;
```

---

## Integração com Meta-Framework (`mf`)

A palavra-chave global `mf` fornece acesso direto aos serviços do runtime:
*   `mf.http.request(...)`: Realiza chamadas de rede.
*   `mf.system.getenv(...)`: Acesso ao sistema (usado pela classe `Env`).
*   `mf.utils.sort(...)`: Algoritmos otimizados em nível nativo.

Esta integração garante que a Corplang tenha performance de linguagem nativa com a facilidade de uma linguagem de script moderna.
