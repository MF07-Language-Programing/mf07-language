# Runtime Architecture

## Overview

The Corplang runtime provides stateful execution of compiled AST nodes without recompilation. It enables:

- **Stateful execution**: Preserve environment between runs
- **Observability**: Track node execution lifecycle
- **Agent management**: Lifecycle control for AI agents
- **Extensibility**: Plugin architecture for AI providers

## Core Components

### 1. AgentManager (`runtime/agent_runtime.py`)

Singleton manager for agent lifecycle:

```python
manager = get_agent_manager()
manager.create_agent(agent_definition_node)
agent_state = manager.get_agent("MyAgent")
```

**State Management:**
- `AgentState`: Container for agent definition, execution count, provider state
- Thread-safe operations with `RLock`
- No AST recompilation required

**Extension Points:**
- `train_agent()`: Integrate AI training logic
- `predict_agent()`: Integrate AI inference
- `embed_agent()`: Integrate embedding generation

### 2. ExecutionManager (`runtime/execution_manager.py`)

Manages stateful execution of AST nodes:

```python
manager = ExecutionManager(interpreter)
context = manager.create_context(file_path="main.mp")
result = manager.execute_node(node, context, observe=True)
```

**Features:**
- Reusable `ExecutionContext` instances
- Environment snapshots
- Observability integration
- Batch node execution

### 3. ObservabilityManager (`runtime/observability.py`)

Event-driven execution tracking:

```python
def my_observer(event: NodeEvent):
    print(f"Node {event.node_type} took {event.elapsed_seconds}s")

obs = get_observability_manager()
obs.register(my_observer)
```

**Event Types:**
- `BEFORE_EXECUTE`: Node starts
- `AFTER_EXECUTE`: Node completes
- `ERROR`: Node raises exception

**Metrics Captured:**
- Execution time
- Node type and location
- Result/error data
- Context snapshots

### 4. IntelligenceProvider (`runtime/intelligence.py`)

Abstract contract for AI integration:

```python
class MyProvider(IntelligenceProvider):
    def initialize(self, config: IntelligenceConfig):
        # Load model, configure API
        pass
    
    def invoke(self, messages, context):
        # Call LiteLLM/Ollama/custom backend
        return "response"
```

**Provider Registry:**
```python
registry = get_provider_registry()
registry.register("litellm", LiteLLMProvider)
provider = registry.create("litellm", config)
```

## Execution Flow

### Agent Definition

1. **Parse** → AST (`AgentDefinition` node)
2. **Register** → `AgentManager.create_agent(node)`
3. **Store** → `AgentState` with definition reference

### Agent Execution

1. **Load** → `AgentManager.get_agent(name)`
2. **Execute** → Extract config from `agent.definition`
3. **Invoke** → Call `IntelligenceProvider.invoke()`
4. **Track** → Emit observability events

### Context Reuse

```python
# Compile once
program = parser.parse("main.mp")

# Execute multiple times with state preservation
manager = ExecutionManager(interpreter)
context = manager.create_context()

result1 = manager.execute_program(program, context)
result2 = manager.execute_program(program, context)  # Reuses variables
```

## Extension Guidelines

### Adding AI Provider

1. Implement `IntelligenceProvider` interface
2. Register with `ProviderRegistry`
3. Update `AgentManager` to use provider

### Adding Observability

1. Register callback with `ObservabilityManager`
2. Handle `NodeEvent` in callback
3. Use `track_execution()` context manager

### Adding Interaction Adapter

1. Implement `InteractionAdapter` interface
2. Use in `loop` command executor
3. Handle input/output for agent

## Design Principles

1. **Immutable AST**: Never modify compiled nodes
2. **Stateful Context**: Environment persists between executions
3. **Observable Execution**: All node execution is trackable
4. **Provider Abstraction**: AI backend is pluggable
5. **Thread Safety**: Singleton managers use locks

## Performance Considerations

- **No recompilation**: AST compiled once, executed many times
- **Minimal overhead**: Observability can be disabled
- **Memory efficient**: Shared root environment
- **Lazy loading**: Providers loaded on-demand

## Integration Points

| Component | Integration Point | Purpose |
|-----------|------------------|---------|
| `AgentDefinitionExecutor` | `AgentManager.create_agent()` | Register agents |
| `AgentPredictExecutor` | `AgentManager.predict_agent()` | Execute inference |
| `Interpreter.execute()` | `ExecutionManager.execute_node()` | Add observability |
| `AgentState.provider_state` | `IntelligenceProvider` instance | Store AI backend |

## Future Extensions

- [ ] Implement LiteLLM provider
- [ ] Add tool calling support (ACL-based)
- [ ] Implement `serve http` FastAPI integration
- [ ] Add persistent agent state (disk/DB)
- [ ] Implement training with DSPy/LoRA
- [ ] Add distributed execution support
---

## Recursos Adicionais

- **Exemplos Práticos**: [STDLIB_EXAMPLES.md](STDLIB_EXAMPLES.md) — Collections, Generics, OOP, Exceptions
- **Implementar Novos Providers**: [guides/intelligence-providers.md](guides/intelligence-providers.md)
- **Esquemas com IA**: [AI_GENERATED_SCHEMAS.md](AI_GENERATED_SCHEMAS.md) — Validação integrada
- **Tutoriais Completos**: [tutorials/INDEX.md](tutorials/INDEX.md) — Do básico ao full-stack