# Exceptions and Try/Catch in CorpLang

This document describes exception handling semantics in CorpLang (.mp) runtime.

## Throwing exceptions
- `throw <expression>` raises an exception whose payload is the evaluated expression.
- The payload can be a string, number, dictionary, or an instance of a class (e.g., `new MyError(...)`).

## Catch clauses and typed matching
- `try { ... } catch (e) { ... }` captures exceptions.
- You can declare typed catches: `catch (e: MyError)` — matching is performed using multiple strategies:
  - Direct match against the exception object's `type` field (e.g., `TypeError`).
  - If the payload is an MP object (instance of a class), its class name is used.
  - Hierarchy/namespace matching: the runtime will search the interpreter global environment for a `ClassObject` with the given name and, if found, will match instances whose declared class equals or inherits from that class.
  - Union types are supported in the catch annotation (e.g., `catch (e: A|B)`).
  - If no type annotation is present, the catch acts as a fallback/last-resort handler.
- If no `catch` clause matches an exception, it is re-thrown upward.

## Exception objects available inside `catch`
- The caught variable (`e` in examples) is an MP exception object (not plain string). It exposes:
  - `type`: string classification (e.g., `CorpLangRaisedException`, `TypeError`)
  - `message`: human-readable message
  - `mpStack`: frozen .mp stack frames at the raise point
  - `internalDiagnostics`: diagnostic report (useful for debugging)
  - Methods: `printStackTrace()`, `printInternalDiagnostics()`
  - For class-based payloads, additional metadata like `payload_class_name` may be present.

## Finally block
- `finally` always runs and can override a return value if it itself executes a `return`.

## Exceptions categories and heuristics
- The runtime maps common Python exceptions to higher-level categories to improve `catch` matching:
  - IO errors (e.g., `FileNotFoundError`, `OSError`) map to **IO_ERROR**
  - Async timeouts (`asyncio.TimeoutError`) map to **CONCURRENCY_ERROR** / **TimeoutError**
  - Memory and assertion failures map to **MEMORY_ERROR** and **ASSERTION_ERROR** respectively
- When an exception is raised from Python internals (e.g., a builtin or `__native__`), the exception is wrapped with diagnostic metadata and the runtime attempts to preserve the original cause. Matchers in `catch (e: <TypeOrCategory>)` will try multiple strategies:
  - Match against `e.type` (the specific exception name)
  - Match against `e.payload_class_name` for class-based payloads
  - Match against `e.error_category` when available (e.g., `IO_ERROR`, `CONCURRENCY_ERROR`)
  - Heuristic fallback: search `e.message` for substrings like `no such file` or `timed out` and match `IO_ERROR` or `TimeoutError` respectively

## Examples
- See `examples/new_main/try_catch_demo.mp`, `examples/new_main/custom_exception_demo.mp`.
- IO and timeout demos: `examples/new_main/io_error_demo.mp`, `examples/new_main/timeout_demo.mp`, `examples/new_main/combined_error_demo.mp`, and `examples/new_main/raise_file_demo.mp`.

## Notes for implementers
- Matching logic lives in `src/corplang/executor/nodes/control_flow.py` and uses `src/corplang/tools/diagnostics.wrap_as_mp_exception` to produce the caught object.
- The match algorithm attempts multiple strategies (direct type, payload class name, interpreter global class resolution and parent chain, message substring and category heuristics).