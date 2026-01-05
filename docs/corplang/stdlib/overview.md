# Biblioteca Padrão Corplang (Stdlib)

A `stdlib/core` da Corplang fornece um conjunto essencial de ferramentas e abstrações para o desenvolvimento de software corporativo moderno, com foco em segurança, tipos e integração nativa com IA.

## Organização dos Módulos

A biblioteca está organizada em sub-módulos lógicos:

### [Collections (Coleções)](./collections.md)
Estruturas de dados fundamentais com suporte a tipos genéricos e verificação em tempo de execução.
*   `List<T>`: Lista dinâmica genérica.
*   `ImmutableList<T>`: Lista imutável que retorna cópias em atualizações.
*   `ICollection<T>`: Interface base para todas as coleções.

### [System & Base (Sistema e Tipos Base)](./system_base.md)
Interação com o sistema operacional e tipos numéricos avançados.
*   `Env`: Helper para variáveis de ambiente.
*   `BigInt`: Suporte a inteiros de precisão arbitrária.

### [Text & Serialization](./serialization.md)
Manipulação de texto e conversão de dados.
*   `Template`: Motor de renderização de templates leve.
*   `JSON` / `YAML`: Serialização de dados corporativos.

### [AI & Agents (IA e Agentes)](./agents_runtime.md)
O núcleo do suporte a IA na Corplang.
*   Definições de Agentes de alto nível.
*   Integração com o `runtime` da Meta-Framework (mf).

## Filosofia da Stdlib

1.  **Segurança em Primeiro Lugar**: Coleções validam tipos para evitar erros comuns de runtime.
2.  **Abstração de IA**: Interagir com modelos de linguagem é tão simples quanto chamar um método em uma classe tradicional.
3.  **Portabilidade**: A `stdlib` é projetada para rodar consistentemente sobre o runtime da MF07.

---
*Este documento faz parte da documentação técnica do projeto MF07 Corplang.*
