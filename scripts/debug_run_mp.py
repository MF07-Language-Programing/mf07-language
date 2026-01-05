import logging
import asyncio
from src.corplang.executor import parse_file, execute

# Silence verbose asyncio internal debug logs (selector reports etc.)
logging.getLogger("asyncio").setLevel(logging.WARNING)
try:
    loop = asyncio.get_running_loop()
    loop.set_debug(False)
except RuntimeError:
    try:
        tmp = asyncio.new_event_loop()
        tmp.set_debug(False)
        tmp.close()
    except Exception:
        pass
except Exception:
    pass

path = "examples/new_main/main.mp"
root = parse_file(path)
print("Top-level statements:")
for i, s in enumerate(getattr(root, "statements", [])):
    print(i, type(s).__name__, getattr(s, "name", None))

print("\n--- Executing statements individually (debug) ---")
from src.corplang.executor.context import ExecutionContext, Environment
from src.corplang.executor.interpreter import Interpreter
interp = Interpreter()
env = Environment()
ctx = ExecutionContext(interpreter=interp, environment=env, memory_manager=None, security_manager=None, pattern_matcher=None)
from src.corplang.executor import execute as top_execute

print('\n--- Now executing whole program with top-level execute() ---')
try:
    top_execute(root)
except Exception as e:
    print('top_execute raised:', e)

print('\n--- Environment after execute (top-level) ---')
try:
    # Re-parse and run to fetch module env
    ast = root
    interp2 = Interpreter()
    env2 = Environment()
    ctx2 = ExecutionContext(interpreter=interp2, environment=env2, memory_manager=None, security_manager=None, pattern_matcher=None)
    interp2.execute(ast, ctx2)
    print('env2 vars:', list(env2.variables.keys()))
except Exception as e:
    print('post-exec raise:', e)

print('--- Done')
