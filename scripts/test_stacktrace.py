import subprocess, os, sys

p = subprocess.run([sys.executable, "scripts/run_mp.py", "examples/new_main/stack_trace_demo.mp"], env=dict(os.environ, PYTHONPATH='.'), capture_output=True, text=True)
print(p.stdout)
print(p.stderr)
# Basic assertions
assert "StackTrace (.mp):" in p.stdout
assert "stack_trace_demo.mp" in p.stdout or "stack_trace_demo.mp" in p.stderr
print('stacktrace demo output looks good')
