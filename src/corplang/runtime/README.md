# Runtime minimal integration

This folder contains lightweight runtime components used to integrate
intelligence providers with the execution environment.

Key ideas:
- Providers return structured `ExecutionResult` objects describing actions
  the runtime can perform (run_code, write_file, log, finalize,...).
- A `CodeRunner` PoC executes Python snippets and returns execution metadata.
- `AgentManager` orchestrates provider invocation and action processing.

Security: the `CodeRunner` is a PoC and is NOT a secure sandbox. For
production use, execute untrusted code in an isolated process / container
with strict limits.
