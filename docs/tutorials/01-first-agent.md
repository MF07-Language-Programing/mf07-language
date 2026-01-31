# Tutorial 1 — Seu Primeiro Agente Autônomo (25 min)

Em Corplang, **agentes não são plugins — são primitivas nativas**. Este tutorial mostra como criar um agente autônomo que toma decisões sem recompilar a AST.

## O Que Você Aprenderá

- Definição de agentes com `agent { }`
- Configuração de providers (local ou remoto)
- Invocação nativa: `invoke self with`
- Persistência de contexto entre chamadas
- Integração com type system

## Pré-requisitos

- Corplang instalado (`mf --version`)
- Para providers **locais**: Ollama instalado e executando (`ollama serve`)
- Para providers **remotos**: Chave API (OpenAI, Anthropic, etc.)

---

## Parte 1: Setup (5 min)

### Criar Projeto

```bash
mf init meu_assistente
cd meu_assistente
```

Estrutura criada:

```
meu_assistente/
├── main.mp                  # Código principal
├── language_config.yaml     # Configuração da linguagem
├── README.md
└── lib/                     # Biblioteca interna
```

### Configurar Provider

Abra `language_config.yaml`:

```yaml
corplang:
  version: "0.1.0"
  name: "meu_assistente"

intelligence:
  provider: "ollama"          # "ollama" | "openai" | "anthropic"
  config:
    base_url: "http://localhost:11434"  # Para Ollama local
    model: "llama2"
    temperature: 0.7
    
# Para providers remotos (OpenAI):
# intelligence:
#   provider: "openai"
#   config:
#     api_key: "${OPENAI_API_KEY}"  # Use variáveis de ambiente
#     model: "gpt-4"
#     temperature: 0.7
```

Se preferir **provider remoto**, defina variável de ambiente:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Parte 2: Definir Agente (8 min)

Crie `main.mp`:

```mp
agent Assistente {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.7
  }
  
  fn processar(pergunta: text) -> text {
    # invoke self: O agente "pensa" sobre a pergunta
    # Mantém contexto com mensagens anteriores automaticamente
    let resposta = invoke self with pergunta
    return resposta
  }
  
  fn processar_com_contexto(pergunta: text, contexto: text) -> text {
    # Você pode fornecer contexto explícito
    let prompt = contexto + "\n\nPergunta: " + pergunta
    let resposta = invoke self with prompt
    return resposta
  }
}

fn main() {
  let assistente = new Assistente()
  
  # Primeira chamada
  let resp1 = assistente.processar("Qual é a capital do Brasil?")
  println("Resposta 1: " + resp1)
  
  # Segunda chamada — o agente lembra do contexto!
  let resp2 = assistente.processar("E qual é sua população?")
  println("Resposta 2: " + resp2)
  
  # Fornecendo contexto explícito
  let contexto = "Você é um especialista em história brasileira."
  let resp3 = assistente.processar_com_contexto(
    "Conte sobre a independência do Brasil",
    contexto
  )
  println("Resposta 3: " + resp3)
}

main()
```

### O que Acontece Aqui

1. **`agent Assistente { }`**: Define um agente nomeado
2. **`config { }`**: Especifica provider e hiperparâmetros
3. **`invoke self with`**: Chama o provider de IA nativo ao runtime
4. **Contexto automático**: Corplang mantém histórico de mensagens entre chamadas
5. **Type safety**: `(pergunta: text) -> text` — O compilador valida tipos

---

## Parte 3: Executar (5 min)

### Ollama Local

Se estiver usando **Ollama**:

```bash
# Terminal 1: Inicie Ollama
ollama serve

# Terminal 2: Baixe um modelo (primeira vez)
ollama pull llama2

# Terminal 3: Execute Corplang
cd meu_assistente
mf run main.mp
```

Saída esperada:

```
Resposta 1: Brasília é a capital do Brasil, localizada no Planalto Central...
Resposta 2: A população de Brasília é de aproximadamente 3 milhões de habitantes...
Resposta 3: A independência do Brasil ocorreu em 7 de setembro de 1822...
```

### Provider Remoto (OpenAI)

```bash
# Defina a chave
export OPENAI_API_KEY="sk-..."

# Execute (sem precisar de Ollama)
mf run main.mp
```

---

## Parte 4: Entender o Fluxo (7 min)

### Arquitetura Interna

```
┌─────────────────────────────────────────────────┐
│ Código Corplang (main.mp)                       │
│                                                 │
│  assistant.processar("Pergunta")                │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ Runtime — AgentManager                          │
│                                                 │
│  1. Carrega definição do agente                │
│  2. Recupera contexto anterior                 │
│  3. Prepara prompt com histórico               │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ IntelligenceProvider (Ollama/OpenAI/Anthropic) │
│                                                 │
│  invoke(messages, context)                     │
│  → Retorna resposta gerada                     │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ AgentState                                      │
│                                                 │
│  • Salva histórico de mensagens                │
│  • Atualiza provider_state                     │
│  • Mantém execution_count                      │
└─────────────────────────────────────────────────┘
```

**Ponto-chave:** Nenhuma recompilação acontece. O AST é compilado uma vez; apenas o estado do agente muda.

---

## Parte 5: Observabilidade (5 min)

Adicione rastreamento ao seu agente:

```mp
from core.runtime.observability import get_observability_manager, NodeEvent

fn my_observer(event: NodeEvent) -> void {
  if event.node_type == "AgentPredictExecutor" {
    println("[AGENT] Tempo: " + event.elapsed_seconds + "s")
  }
}

fn main() {
  let obs = get_observability_manager()
  obs.register(my_observer)
  
  let assistente = new Assistente()
  let resposta = assistente.processar("Olá!")
  println(resposta)
}

main()
```

Saída:

```
[AGENT] Tempo: 1.234s
Olá! Como posso ajudá-lo hoje?
```

---

## Próximas Etapas

1. **Entender contexto compartilhado**: Como o agente mantém histórico?
   → Veja [Arquitetura do Runtime](../runtime_architecture.md#agentstate)

2. **Múltiplos agentes**: Como coordenar dois agentes?
   → Próximo tutorial: [Multi-Agent Routing](02-multi-agent-routing.md)

3. **Implementar novo provider**: Quer usar Claude em vez de GPT-4?
   → Guia: [Custom Intelligence Providers](../guides/intelligence-providers.md)

---

## Troubleshooting

| Problema | Solução |
|----------|---------|
| `ConnectionError: Ollama unavailable` | Verifique: `curl http://localhost:11434` |
| `API key invalid` | Revise env var: `echo $OPENAI_API_KEY` |
| `Agent timeout (>30s)` | Aumente timeout em `language_config.yaml`: `timeout: 60` |
| `Out of memory` | Use modelo menor: `ollama pull neural-chat` (3GB vs 7GB) |

---

## Referência: Agent Lifecycle

```
┌──────────────────────────────────────────┐
│ 1. PARSE: agent { } → AgentDefinition   │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ 2. REGISTER: AgentManager.create_agent() │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ 3. STATE: AgentState com metadata       │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ 4. INVOKE: IntelligenceProvider.invoke() │
└──────────────────┬───────────────────────┘
                   ▼
┌──────────────────────────────────────────┐
│ 5. OBSERVE: ObservabilityManager.emit()  │
└──────────────────────────────────────────┘
```

---

**Parabéns!** Você criou seu primeiro agente autônomo. 

Próximo: [Tutorial 2 — Multi-Agent Routing](02-multi-agent-routing.md) (30 min)
