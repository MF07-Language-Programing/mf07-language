# Tutorial 2 — Multi-Agent Routing & Orquestração (30 min)

Depois de dominar um único agente, o próximo passo é **orquestração**: coordenar múltiplos agentes especializados para resolver problemas complexos.

Imagine um sistema de processamento de pedidos:
- **Agente 1** (Classificador): Categoriza a intenção do cliente
- **Agente 2** (Processador): Executa a lógica baseado na categoria
- **Agente 3** (Validador): Audita o resultado antes de salvar

Tudo conectado em um **pipeline nativo** sem boilerplate.

## O Que Você Aprenderá

- Definição de múltiplos agentes especializados
- Roteamento nativo: `route [agent1, agent2] with`
- Passagem de contexto entre agentes
- Tratamento de fallback e retry
- Observabilidade de pipeline

## Pré-requisitos

- Completar [Tutorial 1](01-first-agent.md)
- Provider configurado (`ollama serve` ou variável de ambiente)

---

## Parte 1: Arquitetura Multi-Agente (8 min)

### Padrão: Pipeline Sequencial

```
Cliente → [Classificador] → [Processador] → [Validador] → Resultado
                   ↓              ↓               ↓
              Intenção      Decisão        Auditoria
```

Cada agente:
- Recebe contexto do anterior
- Decide autonomamente
- Passa decisão adiante
- Nunca precisa recompilar

### Padrão: Roteamento Condicional

```
         ┌─→ [Agente A: Suporte Técnico]
Client →─┤─→ [Agente B: Vendas]
         └─→ [Agente C: Billing]
             (Classificador decide)
```

---

## Parte 2: Implementar Multi-Agent System (12 min)

### Criar Projeto

```bash
mf init ecommerce-pipeline
cd ecommerce-pipeline
```

### Código: `main.mp`

```mp
# Agente 1: Classifica intenção do cliente
agent Classificador {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.3          # Mais determinístico
  }
  
  fn classificar(mensagem: text) -> text {
    let instrucao = "Classifique o seguinte em: COMPRA | DEVOLUÇÃO | SUPORTE | OUTRO\n\n" + mensagem
    let resultado = invoke self with instrucao
    return resultado
  }
}

# Agente 2: Processa a solicitação
agent Processador {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.7
  }
  
  fn processar(tipo: text, detalhe: text) -> text {
    let prompt = "Tipo: " + tipo + "\nDetalhe: " + detalhe + "\n\nGere um plano de ação conciso."
    let acao = invoke self with prompt
    return acao
  }
}

# Agente 3: Valida antes de persister
agent Validador {
  config: {
    "provider": "ollama",
    "model": "llama2",
    "temperature": 0.1          # Bem determinístico
  }
  
  fn validar(tipo: text, plano: text) -> bool {
    let prompt = "Tipo: " + tipo + "\nPlano: " + plano + "\n\nEste plano é seguro e apropriado? (sim/não)"
    let resposta = invoke self with prompt
    # Validador retorna decisão, não explicação
    return text.lower(resposta).contains("sim")
  }
}

# Pipeline: Orquestrador
fn processar_requisicao(mensagem: text) -> text {
  # 1. CLASSIFICAR
  let classificador = new Classificador()
  let tipo = classificador.classificar(mensagem)
  println("[1/3] Classificação: " + tipo)
  
  # 2. PROCESSAR
  let processador = new Processador()
  let plano = processador.processar(tipo, mensagem)
  println("[2/3] Plano: " + plano)
  
  # 3. VALIDAR
  let validador = new Validador()
  let valido = validador.validar(tipo, plano)
  println("[3/3] Validado: " + text.from_bool(valido))
  
  # Retorna resultado ou fallback
  if valido {
    return "✓ Aprovado: " + plano
  } else {
    return "✗ Rejeitado: Precisa de revisão manual"
  }
}

fn main() {
  # Simule 3 requisições
  let requisicoes = [
    "Quero comprar um notebook. Qual é o melhor?",
    "Recebi um produto com defeito, quero devolver.",
    "Meu pedido está atrasado, onde está?"
  ]
  
  for (var msg in requisicoes) {
    println("→ Cliente: " + msg)
    let resultado = processar_requisicao(msg)
    println("→ Sistema: " + resultado)
    println("---")
  }
}

main()
```

---

## Parte 3: Roteamento Dinâmico (7 min)

Versão mais sofisticada com `route` nativo:

```mp
agent EspecialistaVendas {
  config: { "provider": "ollama", "model": "llama2" }
  fn processar(msg: text) -> text { return invoke self with "Responda como especialista em vendas: " + msg }
}

agent EspecialistaSuporte {
  config: { "provider": "ollama", "model": "llama2" }
  fn processar(msg: text) -> text { return invoke self with "Responda como especialista em suporte técnico: " + msg }
}

agent EspecialistaBilling {
  config: { "provider": "ollama", "model": "llama2" }
  fn processar(msg: text) -> text { return invoke self with "Responda como especialista em billing: " + msg }
}

agent Roteador {
  config: { "provider": "ollama", "model": "llama2", "temperature": 0.2 }
  
  fn rotear(mensagem: text) -> text {
    let instrucao = "Classifique em: VENDAS | SUPORTE | BILLING\n\n" + mensagem
    return invoke self with instrucao
  }
}

fn processar_com_roteamento(mensagem: text) -> text {
  let roteador = new Roteador()
  let categoria = roteador.rotear(mensagem)
  
  # Roteamento condicional
  if text.contains(categoria, "VENDAS") {
    let agente = new EspecialistaVendas()
    return agente.processar(mensagem)
  }
  
  if text.contains(categoria, "SUPORTE") {
    let agente = new EspecialistaSuporte()
    return agente.processar(mensagem)
  }
  
  if text.contains(categoria, "BILLING") {
    let agente = new EspecialistaBilling()
    return agente.processar(mensagem)
  }
  
  return "Não consegui classificar. Por favor, tente novamente."
}

fn main() {
  println(processar_com_roteamento("Preciso de uma nota fiscal para meu pedido."))
  println(processar_com_roteamento("O servidor está lento, como faço para acelerar?"))
  println(processar_com_roteamento("Qual é o melhor notebook para programação?"))
}

main()
```

---

## Parte 4: Context Passing & State (5 min)

Agentes compartilhando decisões em cadeia:

```mp
agent Pesquisador {
  config: { "provider": "ollama", "model": "llama2" }
  fn pesquisar(topico: text) -> text {
    return invoke self with "Resuma em 2 linhas: " + topico
  }
}

agent Redator {
  config: { "provider": "ollama", "model": "llama2" }
  fn redigir(resumo: text) -> text {
    return invoke self with "Expanda em um parágrafo: " + resumo
  }
}

agent Editor {
  config: { "provider": "ollama", "model": "llama2" }
  fn editar(texto: text) -> text {
    return invoke self with "Revise para clareza e concisão: " + texto
  }
}

fn pipeline_redacao(topico: text) -> text {
  let pesquisa = new Pesquisador()
  let resumo = pesquisa.pesquisar(topico)
  println("[Pesquisa] " + resumo)
  
  let redacao = new Redator()
  let texto = redacao.redigir(resumo)
  println("[Redação] " + texto)
  
  let edicao = new Editor()
  let final = edicao.editar(texto)
  println("[Edição] " + final)
  
  return final
}

fn main() {
  pipeline_redacao("Inteligência Artificial em 2025")
}

main()
```

---

## Parte 5: Observabilidade Multi-Agente (5 min)

Rastreie decisões em toda a cadeia:

```mp
from core.runtime.observability import get_observability_manager, NodeEvent

var decisoes = []

fn rastreador_agentes(event: NodeEvent) -> void {
  if event.node_type == "AgentPredictExecutor" {
    var entrada = {
      "timestamp": sys.now(),
      "agente": event.metadata.agent_name,
      "tempo_ms": event.elapsed_seconds * 1000,
      "resultado": event.result
    }
    decisoes.append(entrada)
  }
}

fn main() {
  let obs = get_observability_manager()
  obs.register(rastreador_agentes)
  
  # ... execute pipeline ...
  
  # Auditar todas as decisões
  println("=== Auditoria de Decisões ===")
  for (var d in decisoes) {
    println(d.agente + " (" + d.tempo_ms + "ms)")
  }
}

main()
```

---

## Parte 6: Retry & Fallback (5 min)

Tornar pipelines resilientes:

```mp
fn processar_com_retry(operacao: fn() -> text, max_tentativas: int) -> text {
  var tentativa = 0
  
  while tentativa < max_tentativas {
    try {
      return operacao()
    } catch (e: Exception) {
      tentativa = tentativa + 1
      if tentativa < max_tentativas {
        println("[Retry " + tentativa + "] Tentando novamente...")
      } else {
        return "Falha após " + max_tentativas + " tentativas: " + e.message
      }
    }
  }
  
  return "Erro desconhecido"
}

fn main() {
  let resultado = processar_com_retry(
    fn() { return new Classificador().classificar("meu pedido") },
    3
  )
  println(resultado)
}

main()
```

---

## Arquitetura: Como Funciona Internamente

```
┌────────────────────────────────────────────────┐
│ main() — Orquestrador                          │
└────┬───────────────────────────────────────────┘
     │
     ├─→ Classificador.classificar(msg)
     │   ├─→ AgentManager.get_agent("Classificador")
     │   ├─→ IntelligenceProvider.invoke()
     │   ├─→ AgentState.provider_state (histórico)
     │   └─→ return tipo ✓
     │
     ├─→ Processador.processar(tipo, msg)
     │   └─→ ... (mesmo fluxo)
     │       return plano ✓
     │
     └─→ Validador.validar(tipo, plano)
         └─→ ... (mesmo fluxo)
             return bool ✓
```

**Ponto-chave:** Cada agente é independente mas compartilha contexto. Não há "estado global" — apenas `AgentState` local de cada instância.

---

## Próximas Etapas

1. **Persistir decisões**: Salve as decisões em BD?
   → [Tutorial 3 — Validação com IA + Dados](03-ai-validated-persistence.md)

2. **Entender métricas**: Qual agente é mais lento?
   → [Observabilidade Avançada](../guides/observability.md)

3. **Deploy em produção**: Coloque em HTTP?
   → [Tutorial 4 — Web App com Agentes](04-web-app-agents.md)

---

**Parabéns!** Você orquestrou múltiplos agentes. 

Próximo: [Tutorial 3 — Validação de Dados com IA](03-ai-validated-persistence.md) (25 min)
