# Nós da AST (Árvore de Sintaxe Abstrata)

Este documento descreve a estrutura da Árvore de Sintaxe Abstrata (AST) utilizada no compilador Corplang. Todos os nós herdam de uma classe base `ASTNode`, que garante a rastreabilidade obrigatória de cada elemento do código.

## Estrutura Base

### ASTNode
A classe base para todos os nós da árvore.
- `line` (int): Número da linha no código-fonte.
- `column` (int): Número da coluna onde o nó se inicia.
- `file_path` (string, opcional): Caminho para o arquivo de origem.
- `parent` (ASTNode, opcional): Referência ao nó pai na hierarquia.

---

## Estrutura Global e Declarações

### Program
O nó raiz da AST, representando um arquivo completo.
- `statements` (Lista de ASTNode): Declarações de nível superior.
- `docstring` (string, opcional): Documentação do módulo.

### VarDeclaration
Declara uma nova variável.
- `name` (string): Nome da variável.
- `value` (ASTNode): Valor inicial atribuído.
- `type_annotation` (string, opcional): Tipo explícito da variável.

### FunctionDeclaration
Define uma função ou procedimento (usando `intent` ou `fn`).
- `name` (string): Nome da função.
- `params` (Lista de string): Nomes dos parâmetros.
- `body` (Lista de ASTNode): Corpo da função.
- `is_async` (boolean): Flag indicando se a função é assíncrona.
- `return_type` (string, opcional): Tipo de retorno declarado.
- `generic_params` (Lista de string, opcional): Parâmetros de tipo genérico (ex: `<T>`).

---

## Programação Orientada a Objetos

### ClassDeclaration
Define uma estrutura de classe ou driver.
- `name` (string): Nome da classe.
- `body` (Lista de ASTNode): Métodos e campos da classe.
- `extends` (string, opcional): Nome da classe base.
- `implements` (Lista de string, opcional): Lista de interfaces ou contratos implementados.
- `is_abstract` (boolean): Flag para classes abstratas.
- `is_driver` (boolean): Flag indicando se é uma definição de `driver`.

### MethodDeclaration
Representa um método dentro de uma classe.
- `name` (string): Nome do método.
- `params` (Lista de string): Nomes dos parâmetros.
- `is_static` (boolean): Se o método é estático.
- `is_private` (boolean): Se o método é privado.
- `return_type` (string, opcional): Tipo de retorno.

---

## Fluxo de Controle

### IfStatement
- `condition` (ASTNode): Expressão a ser avaliada.
- `then_stmt` (Lista de ASTNode): Executado se verdadeiro.
- `else_stmt` (Lista de ASTNode, opcional): Executado se falso.

### ForStatement
Representa um loop `for` tradicional estilo C.
- `init` (ASTNode, opcional): Inicialização (ex: `var i = 0`).
- `condition` (ASTNode, opcional): Condição de continuação.
- `update` (ASTNode, opcional): Incremento/Atualização.
- `body` (Lista de ASTNode): Corpo do loop.

---

## Agentes e Inteligência Artificial

### AgentDefinition
Define um Agente de IA com capacidades específicas.
- `name` (string): Nome do agente.
- `intelligence`: Bloco de configuração de IA (provedor, capacidades).
- `context`: Restrições de segurança e ferramentas permitidas.
- `execution`: Estratégia de execução (async, cache).
- `authentication`: Configurações de segurança do endpoint (CORS, Rate Limit, IPs).

### ServeStatement
Inicia um servidor para expor agentes ou funcionalidades.
- `adapter` (string): Tipo de servidor (ex: `http`).
- `port` (int, opcional): Porta de escuta.
- `name` (string, opcional): Nome do serviço.
- `agent_names` (Lista de string): Agentes expostos por este servidor.
