# MF07 example: myproject

Projeto de demonstração focado em boas práticas para MF07 e em como cada nó da AST aparece na prática.

## Rodar

```bash
D:/users/Lucas/companys/Imovel Periciado Sistemas/programing-language/mf.py run main.mp
```

## O que este exemplo mostra
- Declaração de `interface` e implementação com `class` (AST: InterfaceDeclaration, ClassDeclaration, MethodDeclaration).
- Herança com `extends` respeitando tipos de retorno e parâmetros.
- Uso de interpolação de strings (`f"...{expr}..."`, AST: InterpolatedString).
- Funções puras com anotação de tipos (AST: FunctionDeclaration, ReturnStatement).
- Uso de logger oficial (`Logger`, `LogLevel`) para diagnóstico.

## Como adicionar novos nós de interpretação
1) Criar/estender o nó na AST em `src/corplang/compiler/lang_ast.py` e garantir parsing em `parser.py`.
2) Registrar o executor correspondente em `src/corplang/runtime/executors/` (implemente `can_execute`/`execute` e registre no `register`).
3) Se o nó tiver implicações de tipos, valide no `type_checker.py` (inferência e regras de compatibilidade).
4) Adicione um exemplo mínimo aqui em `main.mp` para validar o comportamento.

## Boas práticas aplicadas
- Docstrings curtas explicam cada construção.
- Tipos explícitos em métodos que são expostos a outras classes ou interfaces.
- Interpolação de strings para logs e saídas amigáveis.

## Mais recursos
- `language_config.yaml` demonstra configuração do kit de IA básico (pipeline sklearn salvo em `models/basic_kit_pipeline.joblib`).