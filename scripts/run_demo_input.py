import os
from src.corplang.executor import parse_file
from src.corplang.executor.interpreter import Interpreter
from src.corplang.executor.context import ExecutionContext, Environment

# Set MF_INPUTS env var for non-interactive run if not provided
# Format: values separated by '|'
if not os.environ.get('MF_INPUTS'):
    os.environ['MF_INPUTS'] = '4|3.14|y'

interp = Interpreter()
from src.corplang.executor.nodes import statements, expressions, functions, control_flow, oop
for mod in (statements, expressions, functions, control_flow, oop):
    register_fn = getattr(mod, "register", None)
    if callable(register_fn):
        register_fn(interp.registry)

env = Environment()
ctx = ExecutionContext(interpreter=interp, environment=env, memory_manager=None, security_manager=None, pattern_matcher=None)
interp.global_env = ctx.environment
from src.corplang.executor import builtins
builtins.setup_builtins(interp)
interp.root_context = ctx
interp.strict_types = True

ast = parse_file('examples/new_main/interactive_demo.mp')
interp.execute(ast, ctx)
