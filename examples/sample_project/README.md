Sample project for CorpLang / MF07

This example demonstrates several language features implemented in the repository:

- Imports (module resolution relative to the importing file)
- Async/await (async functions returning background tasks)
- Dataset and Model operations (simulated behavior)
- JSON objects and property access (e.g. `obj.name`)

Files:
- `main.mp` - demo script showing imports, async/await, dataset/model calls, JSON objects.
- `lib/utils.mp` - utility functions (greet, sum wrapper).
- `lib/math_helpers.mp` - math helpers.

How to run (from repository root):

Windows (cmd):
```
run_py.bat -m mf examples\\sample_project\\main.mp
```

Notes and changes made to support the example:
- Import resolution: imports are resolved relative to the directory of the importing file; the resolver also walks up parent directories so `import lib.utils` in `examples/sample_project` will find `examples/sample_project/lib/utils.mp`.
- Async tasks: the interpreter will wait for any async tasks returned by top-level statements before exiting.
- Dataset/model: operations are simulated; `dataset load users("users.csv")` will populate an in-memory dataset called `users`.
- Property access: supports `obj.prop` to access object (dict) keys.

If you want a reproducible test, run the pytest test added at the repo root:
```
run_py.bat -m pytest -q
```
