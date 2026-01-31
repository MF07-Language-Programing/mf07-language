# Mapa de Documentação — Guia de Navegação

A documentação de Corplang foi reorganizada para enfatizar **Inteligência Autônoma** como core da linguagem. Use este mapa para encontrar exatamente o que você precisa.

---

## 🚀 Comece Aqui

### Primeiro Contato
- **[README.md](../README.md)** — Visão geral, instalação, pilares de design
- **[Tutorial 1: Seu Primeiro Agente](tutorials/01-first-agent.md)** (25 min) — Crie um agente em 5 minutos

### Essencial para Todo Dev
- **[Tutorial Index](tutorials/INDEX.md)** — Progressão estruturada (nível 1-4)
- **[STDLIB_EXAMPLES.md](STDLIB_EXAMPLES.md)** — Copy-paste pronto (Collections, Generics, OOP)

---

## 🧠 Agentes & IA (Core da Linguagem)

### Tutoriais Progressivos
1. **[Tutorial 1: Seu Primeiro Agente](tutorials/01-first-agent.md)** (25 min)
   - Criar agente
   - Configurar provider (Ollama/OpenAI)
   - Invocar com `invoke self`
   - Persistência de contexto

2. **[Tutorial 2: Multi-Agent Routing](tutorials/02-multi-agent-routing.md)** (30 min)
   - Múltiplos agentes especializados
   - Roteamento condicional
   - Passagem de contexto
   - Observabilidade

3. **[Tutorial 3: Validação com IA](tutorials/03-ai-validated-persistence.md)** (25 min)
   - Agentes validam dados
   - Pipeline: Validar → Enriquecer → Persistir
   - Auditoria integrada
   - Multi-driver (SQLite → PostgreSQL)

4. **[Tutorial 4: Web App com Agentes](tutorials/04-web-app-agents.md)** (35 min)
   - Servidor HTTP nativo
   - Validação de payload com agentes
   - Tratamento profissional de erro
   - Deploy em produção

### Referência Aprofundada
- **[guides/intelligence-providers.md](guides/intelligence-providers.md)** — Implementar novo provider
  - Exemplo: Ollama (LLM local)
  - Exemplo: LiteLLM (100+ modelos)
  - Exemplo: Custom provider (sua empresa)
  
- **[AI_GENERATED_SCHEMAS.md](AI_GENERATED_SCHEMAS.md)** — Esquemas evoluem com agentes
  - Validação automática
  - Auditoria de decisões
  - Migrações dirigidas por IA

- **[runtime_architecture.md](runtime_architecture.md)** — Arquitetura interna
  - AgentManager
  - ExecutionManager
  - ObservabilityManager
  - IntelligenceProvider contract

---

## 📊 Persistência & Banco de Dados

### Migrations Multi-Driver
- **[MIGRATION_STRATEGY.md](MIGRATION_STRATEGY.md)** — Sistema sequencial de migrações
- **[MIGRATION_EXAMPLES.md](MIGRATION_EXAMPLES.md)** — SQLite vs PostgreSQL
- **[MULTI_DRIVER_MIGRATIONS.md](MULTI_DRIVER_MIGRATIONS.md)** — Referência completa

### Integração IA + Dados
- **[AI_GENERATED_SCHEMAS.md](AI_GENERATED_SCHEMAS.md)** — Agentes validam antes de inserir

### Configuração
- **[DATABASE_CONFIGURATION.md](DATABASE_CONFIGURATION.md)** — Setup de drivers
- **[POSTGRESQL_CONFIG.md](POSTGRESQL_CONFIG.md)** — PostgreSQL específico

---

## 💻 Linguagem & Type System

### Exemplos Práticos
- **[STDLIB_EXAMPLES.md](STDLIB_EXAMPLES.md)** — Copy-paste pronto
  - Collections (List, Map, Set, Stack, Queue)
  - Generics
  - OOP (Classes, Constructors, Generics)
  - Iteration customizada
  - Exception handling
  - Data & Hora
  - String operations

### Recursos Avançados
- **[root_playground_examples.md](root_playground_examples.md)** — Snippets idiomáticos originais

---

## 🎯 Casos de Uso Reais

### Sistema de CRM com Agentes
Veja [Tutorial 3: Validação com IA](tutorials/03-ai-validated-persistence.md)
- Validar dados de cliente
- Categorizar automaticamente
- Auditoria de decisões
- Migrar SQLite → PostgreSQL

### API HTTP com Agentes
Veja [Tutorial 4: Web App com Agentes](tutorials/04-web-app-agents.md)
- Classificação de sentimento
- Validação de payload
- Rate limiting
- Logging estruturado
- Deploy com Docker

---

## 📚 Referência Completa

| Tema | Arquivo | Tipo |
|------|---------|------|
| Instalação | [README.md](../README.md) | Quick start |
| CLI | [README.md](../README.md) | Referência |
| Tutoriais | [tutorials/INDEX.md](tutorials/INDEX.md) | Progressão |
| Agentes | [tutorials/01-first-agent.md](tutorials/01-first-agent.md) | Tutorial |
| Providers | [guides/intelligence-providers.md](guides/intelligence-providers.md) | Guia |
| Esquemas | [AI_GENERATED_SCHEMAS.md](AI_GENERATED_SCHEMAS.md) | Guia |
| Runtime | [runtime_architecture.md](runtime_architecture.md) | Arquitetura |
| Migrations | [MIGRATION_STRATEGY.md](MIGRATION_STRATEGY.md) | Referência |
| Stdlib | [STDLIB_EXAMPLES.md](STDLIB_EXAMPLES.md) | Exemplos |
| Versões | [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) | Referência |
| Publish | [PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md) | Guia |
| Uninstall | [UNINSTALL_GUIDE.md](UNINSTALL_GUIDE.md) | Segurança |

---

## 🎓 Percursos de Aprendizado

### Para Iniciantes (Sem IA antes)
1. Leia: [README.md](../README.md) — Entenda a visão
2. Execute: [Tutorial 1](tutorials/01-first-agent.md) — Crie seu primeiro agente (25 min)
3. Estude: [STDLIB_EXAMPLES.md](STDLIB_EXAMPLES.md) — Conheça a sintaxe (30 min)
4. Construa: [Tutorial 2](tutorials/02-multi-agent-routing.md) — Múltiplos agentes (30 min)

**Tempo total: ~1h30m**

### Para Desenvolvedores Backend
1. Execute: [Tutorial 3](tutorials/03-ai-validated-persistence.md) — Dados + IA (25 min)
2. Estude: [AI_GENERATED_SCHEMAS.md](AI_GENERATED_SCHEMAS.md) — Validação (15 min)
3. Consulte: [MIGRATION_STRATEGY.md](MIGRATION_STRATEGY.md) — Evoluir schema (10 min)
4. Deploy: [Tutorial 4](tutorials/04-web-app-agents.md) — HTTP (35 min)

**Tempo total: ~1h25m**

### Para Contribuidores de Providers
1. Leia: [runtime_architecture.md](runtime_architecture.md) — Arquitetura (20 min)
2. Estude: [guides/intelligence-providers.md](guides/intelligence-providers.md) — Implementação (40 min)
3. Implemente: Novo provider (1-2h)
4. Teste: Unitários (30 min)
5. PR: GitHub (contribuição!)

**Tempo total: ~3-4h**

---

## 🔗 Navegar por Tópico

### "Quero aprender IA em Corplang"
→ [Tutorial 1](tutorials/01-first-agent.md) → [Tutorial 2](tutorials/02-multi-agent-routing.md)

### "Quero persistir dados com validação"
→ [Tutorial 3](tutorials/03-ai-validated-persistence.md) → [AI_GENERATED_SCHEMAS.md](AI_GENERATED_SCHEMAS.md)

### "Quero fazer HTTP/API"
→ [Tutorial 4](tutorials/04-web-app-agents.md)

### "Quero integrar meu próprio LLM"
→ [guides/intelligence-providers.md](guides/intelligence-providers.md)

### "Quero entender como funciona internamente"
→ [runtime_architecture.md](runtime_architecture.md)

### "Quero exemplos de código"
→ [STDLIB_EXAMPLES.md](STDLIB_EXAMPLES.md)

### "Quero migrar de dev para produção"
→ [MIGRATION_STRATEGY.md](MIGRATION_STRATEGY.md) → [MIGRATION_EXAMPLES.md](MIGRATION_EXAMPLES.md)

### "Quero publicar meu pacote"
→ [PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md)

### "Quero desinstalar limpo"
→ [UNINSTALL_GUIDE.md](UNINSTALL_GUIDE.md)

---

## 📋 Checklist Rápido

### Setup Inicial
- [ ] Instale Corplang: `curl -fsSL ... | bash`
- [ ] Crie projeto: `mf init meu_projeto`
- [ ] Configure provider em `language_config.yaml`
- [ ] Execute exemplo: `mf run main.mp`

### Antes de Deploy
- [ ] Agentes testados localmente (Ollama)
- [ ] Migrations geradas: `mf db makemigrations`
- [ ] Banco PostgreSQL pronto
- [ ] Variáveis de ambiente setadas
- [ ] Rate limiting configurado
- [ ] Logs estruturados implementados
- [ ] Docker image construída
- [ ] Health checks implementados

---

## 🔍 Busca Rápida

| Eu quero... | Arquivo |
|------------|---------|
| Criar um agente | [tutorials/01-first-agent.md](tutorials/01-first-agent.md) |
| Usar Ollama | [guides/intelligence-providers.md](guides/intelligence-providers.md) |
| Usar OpenAI/Claude | [guides/intelligence-providers.md](guides/intelligence-providers.md) |
| Validar com IA | [tutorials/03-ai-validated-persistence.md](tutorials/03-ai-validated-persistence.md) |
| Fazer HTTP | [tutorials/04-web-app-agents.md](tutorials/04-web-app-agents.md) |
| Exemplo de List/Map | [STDLIB_EXAMPLES.md](STDLIB_EXAMPLES.md) |
| Migrar DB | [MIGRATION_STRATEGY.md](MIGRATION_STRATEGY.md) |
| Entender gerenciamento de versões | [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) |
| Publicar pacote | [PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md) |

---

## 📞 Suporte & Comunidade

- **Issues**: [GitHub Issues](https://github.com/MF07-Language-Programing/mf07-language/issues)
- **Discussões**: [GitHub Discussions](https://github.com/MF07-Language-Programing/mf07-language/discussions)
- **Contribuir**: Fork → Branch → PR
- **Docs melhoradas?** Issue/PR no repo!

---

## 🎉 Pronto para Começar?

**Comece aqui:** [Tutorial 1: Seu Primeiro Agente (25 min)](tutorials/01-first-agent.md)

Ou se preferir aprender pelo exemplo:

```bash
mf init hello-agent
cd hello-agent
# Edite main.mp com o código do Tutorial 1
mf run main.mp
```

**Bem-vindo ao futuro da programação com IA!**
