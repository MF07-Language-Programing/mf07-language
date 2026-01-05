# Interface Visual de Terminal (TerminalUI)

O Corplang inclui um sistema de animação e estilização para CLI inspirado no gerenciador de pacotes `uv`, proporcionando uma experiência de usuário profissional e visualmente agradável durante a compilação e execução de processos.

## Funcionalidades

*   **Renderização Gradual (Slowed Logs)**: Mensagens aparecem de forma progressiva e suave.
*   **Suporte a Temas**: Cores configuráveis e suporte nativo ao tema "uv".
*   **Componentes Visuais**:
    *   Barras de progresso com porcentagem.
    *   Status de ação (ex: `compiling`, `success`, `error`).
    *   Logs coloridos por nível (info, warning, error).
*   **Desacoplamento**: O sistema funciona de forma independente, permitindo fácil integração em qualquer parte do pipeline.

## Configuração (`config.yml`)

As animações podem ser ajustadas na seção `ui` do arquivo de configuração:

```yaml
ui:
  theme: "uv"              # Temas disponíveis: "uv", "dark"
  animation_speed: 0.01    # Segundos de atraso entre caracteres
  enabled: true            # Ativa ou desativa as animações
```

## Uso no Código

### Acesso ao Singleton
```python
from src.corplang.core.ui.terminal import ui
```

### Exemplos de Comandos

#### Status de Ação
```python
ui.status("Compiling", "main.mp")
ui.success("Build completed")
ui.error("Syntax error at line 10")
```

#### Barra de Progresso
```python
ui.progress_bar(50, 100, prefix="Building AST")
```

#### Logs Tradicionais
```python
ui.log("Iniciando análise léxica", level="info")
```

## Temas

### Tema `uv` (Padrão)
Utiliza cores suaves (lavanda, azul suave, verde primavera) otimizadas para terminais modernos que suportam 256 cores.

### Tema `dark`
Utiliza as cores ANSI padrão do terminal (ciano, azul, verde) para maior compatibilidade com terminais antigos.

## Integração com o Compilador

O `Parser` está integrado nativamente com o `TerminalUI`. Quando o `compiler_view` está ativado em `config.yml`, o progresso da criação de nós e o status da compilação são exibidos automaticamente com animações.
