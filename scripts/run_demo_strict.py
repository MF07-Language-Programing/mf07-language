from src.corplang.executor import parse_file
from src.corplang.executor.interpreter import Interpreter

# Create interpreter and register node executors
interp = Interpreter()
from src.corplang.executor.nodes import statements, expressions, functions, control_flow, oop
for mod in (statements, expressions, functions, control_flow, oop):
    register_fn = getattr(mod, "register", None)
    if callable(register_fn):
        register_fn(interp.registry)

# Initialize environment and builtins similar to executor.execute when creating a new interpreter
from src.corplang.executor.context import ExecutionContext, Environment
from src.corplang.executor import builtins
env = Environment()
ctx = ExecutionContext(interpreter=interp, environment=env, memory_manager=None, security_manager=None, pattern_matcher=None)
interp.global_env = ctx.environment
builtins.setup_builtins(interp)
interp.root_context = ctx
interp.current_file = None

# Enable strict types for the demo
interp.strict_types = True

ast = parse_file('examples/new_main/type_demo.mp')
# Execute using our interpreter with the prepared context
interp.execute(ast, ctx)
