# Documentação Técnica Corplang

Bem-vindo à documentação oficial da linguagem **Corplang**. Esta documentação foi projetada para desenvolvedores que desejam entender as entranhas do compilador, utilizar a biblioteca padrão de forma eficiente e dominar a sintaxe orientada a Agentes de IA.

## 🚀 Começando

A Corplang é uma linguagem de programação moderna desenvolvida sobre a Meta-Framework 07 (MF07). Ela se destaca por integrar Inteligência Artificial como uma primitiva do sistema, permitindo que Agentes de IA sejam declarados e operados com a mesma facilidade que classes e funções.

## 📖 Seções da Documentação

### [1. Guia da Linguagem](./language_guide/syntax.md)
Aprenda as bases da Corplang para começar a programar rapidamente.
*   **[Sintaxe Fundamental](./language_guide/syntax.md)**: Variáveis, loops e controle de fluxo.
*   **[Programação Orientada a Objetos](./language_guide/oop.md)**: Classes, interfaces, genéricos e drivers.
*   **[Agentes e IA Nativa](./language_guide/agents_ai.md)**: Como declarar, treinar e expor agentes de IA.

### [2. O Compilador](./compiler/overview.md)
Entenda como o código Corplang é transformado em uma Árvore de Sintaxe Abstrata (AST).
*   **[Lexer](./compiler/lexer.md)**: Análise léxica e detecção de JSON.
*   **[Parser](./compiler/parser.md)**: Arquitetura modular e orquestração.
*   **[Nós da AST](./compiler/nodes.md)**: Estrutura de dados e rastreabilidade.

### [3. Biblioteca Padrão (Stdlib)](./stdlib/overview.md)
Explore as ferramentas prontas para uso que acompanham a linguagem.
*   **[Coleções Tipadas](./stdlib/collections.md)**: Listas genéricas e imutáveis.
*   **[Sistema e Base](./stdlib/system_base.md)**: Variáveis de ambiente e BigInt.
*   **[Serialização e Texto](./stdlib/serialization.md)**: JSON, YAML e Templates.
*   **[IA e Runtime](./stdlib/agents_runtime.md)**: Integração profunda com o runtime `mf`.

### [4. Runtime e Execução](./runtime/interpreter.md)
Entenda como o código é executado após a compilação.
*   **[Interpreter](./runtime/interpreter.md)**: Executor de AST e registry de nós.
*   **[Exceções](./runtime/exceptions.md)**: Sistema de tratamento de erros.

### [5. Sistema Core](./core/loader.md)
Componentes internos que sustentam a linguagem.
*   **[Module Loader](./core/loader.md)**: Carregamento automático de módulos core.
*   **[Module Registry](./core/module_registry.md)**: Cache e registro de módulos.
*   **[Config](./core/config.md)**: Sistema de configuração.
*   **[Tokens](./core/tokens.md)**: Tipos de token do lexer.
*   **[Security](./core/security.md)**: Políticas de segurança.
*   **[Memory](./core/memory.md)**: Gestão de memória.
*   **[Relations](./core/relations.md)**: Sistema de relações entre módulos.

### [6. Ferramentas de Desenvolvimento](./tools/diagnostics.md)
Utilitários para debug e produtividade.
*   **[Diagnostics](./tools/diagnostics.md)**: Formatação profissional de exceções.
*   **[Logger](./tools/logger.md)**: Sistema de logging estruturado.

### [7. Interface de Usuário](./ui/terminal_ui.md)
Sistema de UI para terminal.
*   **[Terminal UI](./ui/terminal_ui.md)**: Animações e estilização profissional no CLI.

## 🛠️ Filosofia do Projeto

*   **Humanizada**: Documentação escrita para pessoas, com exemplos claros e explicações diretas.
*   **Profissional**: Focada em rastreabilidade, segurança de tipos e robustez corporativa.
*   **Funcional**: Cada exemplo de código nesta documentação é compatível com o parser atual da Corplang.
*   **Cordial**: Tom acessível e amigável para desenvolvedores de todos os níveis.

## 🚀 Começando Rápido

### Instalar e executar

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/mf07-language

# Instale dependências
pip install -r requirements.txt

# Execute seu primeiro programa
python scripts/run_mp.py examples/first_project/main.mp
```

### Seu primeiro programa .mp

```corplang
# main.mp
var nome = "Desenvolvedor"

intent saudar(pessoa: string) {
    print("Olá, {pessoa}! Bem-vindo à Corplang!")
}

saudar(nome)
```

## 📚 Recursos adicionais

- **Exemplos práticos**: Veja `/examples` para projetos completos
- **Testes**: Explore `/tests` para casos de uso avançados
- **Stdlib**: Código-fonte em `/src/corplang/stdlib/core`

---
*Equipe de Desenvolvimento MF07 Corplang — Janeiro 2026*
