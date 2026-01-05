import subprocess
import sys
import os

cases = [
    ("examples/new_main/io_error_demo.mp", "caught as IO_ERROR category"),
    ("examples/new_main/timeout_demo.mp", "caught TimeoutError"),
    ("examples/new_main/custom_exception_demo.mp", "caught MyError via typed catch"),
    ("examples/new_main/raise_file_demo.mp", "caught by name: FileNotFoundError"),
]

ok = True
for path, expect in cases:
    print(f"Running {path} ...")
    env = dict(os.environ)
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + ":." if env.get("PYTHONPATH") else "."
    p = subprocess.run([sys.executable, "scripts/run_mp.py", path], capture_output=True, text=True, env=env)
    out = p.stdout + p.stderr
    if expect in out:
        print(f"  OK: found '{expect}'")
    else:
        print("  FAIL: expected '" + expect + "' not found")
        print("--- OUTPUT ---")
        print(out)
        ok = False

if not ok:
    sys.exit(2)
print("All exception demos passed.")
