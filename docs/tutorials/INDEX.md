# Tutorial Index — Corplang

Aprenda Corplang através de uma progressão estruturada, começando com o core da linguagem: **inteligência autônoma**.

---

## Nível 1: Fundamentos de Agentes

### [Tutorial 1 — Seu Primeiro Agente Autônomo (25 min)](01-first-agent.md)
**Por que começar aqui:** Agentes são a primitiva fundamental do Corplang. Este tutorial mostra como criar, configurar e executar um agente que toma decisões autônomas.

**O que você aprenderá:**
- Definição de agentes com `agent { }`
- Configuração de providers (local Ollama ou remoto OpenAI)
- Invocação nativa: `invoke self with`
- Persistência de contexto entre chamadas
- Integração com sistema de tipos

**Próximo:** [Tutorial 2 — Roteamento de Múltiplos Agentes](02-multi-agent-routing.md)

---

## Nível 2: Orquestração Avançada

### [Tutorial 2 — Multi-Agent Routing & Orquestração (30 min)](02-multi-agent-routing.md)
**Por que fazer isso:** Sistemas do mundo real raramente usam um único agente. Este tutorial mostra como coordenar múltiplos agentes especializados em pipelines de dados.

**O que você aprenderá:**
- Criação de agentes especializados (Classificador, Processador, Validador)
- Roteamento nativo: `route [agent1, agent2] with`
- Passagem de contexto entre agentes
- Observabilidade: Rastreamento de decisões
- Tratamento de fallback e retry

**Caso de Uso Real:** Processamento de pedidos de e-commerce — um agente classifica, outro processa, outro valida.

**Próximo:** [Tutorial 3 — Persistência com Validação de IA](03-ai-validated-persistence.md)

---

## Nível 3: Inteligência + Dados

### [Tutorial 3 — Validação de Dados Gerada por IA (25 min)](03-ai-validated-persistence.md)
**Por que fazer isso:** A maioria das aplicações precisa armazenar dados. Corplang integra agentes diretamente no pipeline de persistência — validação não é mais um boilerplate, é raciocínio.

**O que você aprenderá:**
- Definição de modelos com `model { }`
- Validação automática via `AgentPredictExecutor`
- Migrações dirigidas por tipo (SQLite → PostgreSQL)
- Tratamento de conflitos de esquema
- Auditoria: Quem validou? Quando? Por quê?

**Caso de Uso Real:** Sistema de CRM onde cada registro de cliente é validado por um agente antes de ser inserido.

**Próximo:** [Tutorial 4 — Aplicação Web com Agentes](04-web-app-agents.md)

---

## Nível 4: Full-Stack

### [Tutorial 4 — Web App: HTTP Server com Agentes (35 min)](04-web-app-agents.md)
**Por que fazer isso:** Coloque seus agentes em produção. Este tutorial mostra como construir um serviço HTTP que usa agentes para processar requisições, validar payload, e gerar respostas inteligentes.

**O que você aprenderá:**
- Criação de servidor HTTP nativo: `serve http { }`
- Routing de endpoints a agentes específicos
- Validação de payload com `AgentPredictExecutor`
- Tratamento de erro profissional (backpressure, timeouts)
- Logging estruturado e observabilidade

**Caso de Uso Real:** API de análise de sentimento onde cada POST é processado por um agente de classificação.

---

## Referência Rápida

| Tutorial | Foco | Tempo | Pré-requisito |
|----------|------|-------|---|
| [1 — Seu Primeiro Agente](01-first-agent.md) | Fundamentos | 25 min | Nenhum |
| [2 — Multi-Agent Routing](02-multi-agent-routing.md) | Orquestração | 30 min | Tutorial 1 |
| [3 — Validação com IA](03-ai-validated-persistence.md) | Dados + Agentes | 25 min | Tutorial 2 |
| [4 — Web App com Agentes](04-web-app-agents.md) | Full-Stack | 35 min | Tutorial 3 |

---

## Próximos Passos Após Tutoriais

- **Documentação de Referência**: [Arquitetura do Runtime](../runtime_architecture.md)
- **Implementar Novos Providers**: [Guia de IntelligenceProvider](../guides/intelligence-providers.md)
- **Escalar com Persistência**: [Multi-Driver Migrations](../MULTI_DRIVER_MIGRATIONS.md)
- **Exemplo Completo**: Veja `examples/agents/` no repositório
