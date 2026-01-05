# Agentes e IA: O Diferencial Corplang

Diferente de outras linguagens onde a IA é uma biblioteca externa, na Corplang a inteligência artificial é uma primitiva da linguagem.

## Blocos de Definição de Agente

Um agente é definido pelo comando `agent` e possui sub-blocos especializados:

### 1. Intelligence
Configura o "cérebro" do agente.
*   `provider`: O motor de IA (ex: "auto", "openai", "llama").
*   `capability`: O que o agente deve focar (ex: "code", "chat", "analysis").

### 2. Context
Define as fronteiras e ferramentas.
*   `allow`: Permite o acesso a funções (`intents`) ou classes específicas.
*   `deny`: Bloqueia acessos explicitamente.

### 3. Execution
Controla o comportamento operacional.
*   `async`: Execução não bloqueante.
*   `cache_context`: Otimização de tokens ao reutilizar o contexto.

### 4. Authentication & Security
Protege o agente quando exposto como serviço.
*   `rate_limit`: Evita abusos de chamadas.
*   `whitelist_ips` / `blacklist_ips`: Controle de acesso por rede.

---

## O Ciclo de Vida do Agente

### Criação e Treinamento
```corplang
agent Especialista { ... }
agent train Especialista with "dados_locais.json";
```

### Exposição (Serving)
O comando `serve` transforma sua definição em um endpoint funcional instantaneamente.
```corplang
serve http port 8361 name "especialista-v1" using Especialista;
```

### Interação e Loops
Para interações diretas via terminal ou fluxos contínuos:
```corplang
loop stdin using Especialista;
```

---

## Previsão e Inferência (Predict)
Você pode usar agentes diretamente no seu código para tomar decisões ou processar dados:

```corplang
var resposta = agent predict Especialista("Analise este relatório de vendas");
print(resposta);
```

Este comando envia a entrada para o agente, que a processa dentro do seu contexto e ferramentas permitidas, retornando o resultado diretamente para uma variável Corplang.
