# Interactive Console Loop Guide

The `loop stdin using Agent[, Agent, ...]` statement provides a lightweight interactive interface for agent interaction via stdin.

## Basic Usage

```plaintext
agent MyAssistant {
    intelligence { provider auto }
    context { allow intent my_intent }
    execution { interactive true }
}

loop stdin using MyAssistant
```

Type input at the `>` prompt. Exit by typing `exit` or `quit`, or by sending EOF (Ctrl+D on Unix, Ctrl+Z on Windows).

## Multi-Agent Routing

Prefix your message with an agent name and a colon to route to a specific agent:

```plaintext
agent Agent1 { ... }
agent Agent2 { ... }

loop stdin using Agent1, Agent2
```

Then in the loop:
- `Agent1: hello` → routes to Agent1
- `Agent2: hi` → routes to Agent2  
- `hello` → defaults to the first agent (Agent1)

## Output Format

Agent responses are displayed with the agent name prefix if multiple agents are in the loop:

```
[Agent1] response text
[Agent2] another response
```

Single-agent loops omit the prefix for clarity.

## Error Handling

Interaction failures are caught and reported without stopping the loop:

```
> invalid input
Error interacting with agent 'MyAssistant': <error details>
```

This allows graceful recovery and continued interaction.

## Lifecycle

- **Startup**: Agents are compiled and registered on first use.
- **Cleanup**: The adapter is properly closed on exit, ensuring stdin is released.
- **Graceful shutdown**: Ctrl+C or `exit` command cleanly terminates the loop.

## Implementation

- [src/corplang/runtime/interaction.py](../../src/corplang/runtime/interaction.py) — Adapter and routing logic
- [src/corplang/executor/nodes/statements.py](../../src/corplang/executor/nodes/statements.py) — LoopExecutor
