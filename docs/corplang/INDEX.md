# Índice Completo da Documentação Corplang

Este índice organiza toda a documentação disponível para facilitar sua navegação.

## 📖 Por Categoria

### 🧪 Tutoriais Práticos
Aprenda criando sistemas úteis do zero.

- [Tutorial 1 — CLI To‑Do](../tutorials/01-cli-todo.md)
- [Tutorial 2 — HTTP JSON API](../tutorials/02-http-json-api.md)
- [Tutorial 3 — CRUD com SQLite](../tutorials/03-db-crud-sqlite.md)
- [Tutorial 4 — Agente no Console](../tutorials/04-agent-console.md)

### 🎓 Guia da Linguagem
Aprenda a programar em Corplang.

- [Sintaxe Fundamental](./language_guide/syntax.md) - Variáveis, loops, condicionais
- [Programação Orientada a Objetos](./language_guide/oop.md) - Classes, herança, interfaces
- [Agentes e IA Nativa](./language_guide/agents_ai.md) - Declarar e treinar agentes de IA

### 🔧 Compilador
Como o código é transformado em AST.

- [Visão Geral](./compiler/overview.md) - Arquitetura do compilador
- [Lexer](./compiler/lexer.md) - Análise léxica e tokenização
- [Parser](./compiler/parser.md) - Análise sintática e AST
- [Nós da AST](./compiler/nodes.md) - Estrutura dos nós

### 🚀 Runtime e Execução
Como o código é executado.

- [Interpreter](./runtime/interpreter.md) - Executor de AST e registry de nós
- [Exceções](./runtime/exceptions.md) - Sistema de tratamento de erros

### 💎 Sistema Core
Componentes internos da linguagem.

- [Module Loader](./core/loader.md) - Carregamento de módulos core
- [Module Registry](./core/module_registry.md) - Cache de módulos
- [Config](./core/config.md) - Sistema de configuração
- [Tokens](./core/tokens.md) - Tipos de token
- [Security](./core/security.md) - Políticas de segurança
- [Memory](./core/memory.md) - Gestão de memória
- [Relations](./core/relations.md) - Relações entre módulos

### 📦 Biblioteca Padrão (Stdlib)
Módulos prontos para uso.

- [Visão Geral](./stdlib/overview.md) - Organização da stdlib
- [Coleções](./stdlib/collections.md) - List, Map, Set
- [Sistema e Base](./stdlib/system_base.md) - Env, BigInt
- [Serialização](./stdlib/serialization.md) - JSON, YAML, Templates
- [IA e Runtime](./stdlib/agents_runtime.md) - Integração com agentes

#### Módulos Específicos

**Base**
- [BigInt](./stdlib/core/base/bigint.md)
- [Comparators](./stdlib/core/base/comparators.md)
- [Ranges](./stdlib/core/base/ranges.md)

**Coleções**
- [Map](./stdlib/core/map.md)

**Texto**
- [Regex](./stdlib/core/text/regex.md)

**Rede**
- [HTTP](./stdlib/core/net/http.md)

**Utilitários**
- [Assert](./stdlib/core/utils/assert.md)
- [Logger](./stdlib/core/utils/logger.md)
- [UUID](./stdlib/core/utils/uuid.md)
- [Validator](./stdlib/core/utils/validator.md)

**Erros**
- [Exceptions](./stdlib/core/exceptions.md)

### 🛠️ Ferramentas
Utilitários para desenvolvimento.

- [Diagnostics](./tools/diagnostics.md) - Formatação de exceções
- [Logger](./tools/logger.md) - Sistema de logging estruturado

### 🖥️ Interface de Usuário
Sistema de UI para terminal.

- [Terminal UI](./ui/terminal_ui.md) - Animações e estilização CLI

---

## 📑 Por Ordem Alfabética

- [Agentes e IA Nativa](./language_guide/agents_ai.md)
- [Assert](./stdlib/core/utils/assert.md)
- [BigInt](./stdlib/core/base/bigint.md)
- [Coleções](./stdlib/collections.md)
- [Comparators](./stdlib/core/base/comparators.md)
- [Config](./core/config.md)
- [Diagnostics](./tools/diagnostics.md)
- [Exceptions (Runtime)](./runtime/exceptions.md)
- [Exceptions (Stdlib)](./stdlib/core/exceptions.md)
- [HTTP](./stdlib/core/net/http.md)
- [IA e Runtime](./stdlib/agents_runtime.md)
- [Interpreter](./runtime/interpreter.md)
- [Lexer](./compiler/lexer.md)
- [Logger (Tools)](./tools/logger.md)
- [Logger (Stdlib)](./stdlib/core/utils/logger.md)
- [Map](./stdlib/core/map.md)
- [Memory](./core/memory.md)
- [Module Loader](./core/loader.md)
- [Module Registry](./core/module_registry.md)
- [Nós da AST](./compiler/nodes.md)
- [OOP](./language_guide/oop.md)
- [Parser](./compiler/parser.md)
- [Ranges](./stdlib/core/base/ranges.md)
- [Regex](./stdlib/core/text/regex.md)
- [Relations](./core/relations.md)
- [Security](./core/security.md)
- [Serialização](./stdlib/serialization.md)
- [Sintaxe Fundamental](./language_guide/syntax.md)
- [Sistema e Base](./stdlib/system_base.md)
- [Terminal UI](./ui/terminal_ui.md)
- [Tokens](./core/tokens.md)
- [UUID](./stdlib/core/utils/uuid.md)
- [Validator](./stdlib/core/utils/validator.md)
- [Visão Geral (Compilador)](./compiler/overview.md)
- [Visão Geral (Stdlib)](./stdlib/overview.md)

---

## 🔍 Guias Rápidos

### Para iniciantes
1. [Sintaxe Fundamental](./language_guide/syntax.md)
2. [Seu primeiro programa](./README.md#-começando-rápido)
3. [Coleções](./stdlib/collections.md)

### Para desenvolvedores
1. [Compilador - Visão Geral](./compiler/overview.md)
2. [Interpreter](./runtime/interpreter.md)
3. [Module Loader](./core/loader.md)

### Para contributors
1. [Nós da AST](./compiler/nodes.md)
2. [Diagnostics](./tools/diagnostics.md)
3. [Logger](./tools/logger.md)

---

**Última atualização**: Janeiro 2026  
**Versão da documentação**: 1.0
