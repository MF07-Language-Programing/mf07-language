"""Minimal code runner PoC for executing provider actions.

This is NOT a secure sandbox. It is a practical PoC to execute Python
snippets returned by a provider. For production, run code in an
isolated process/container with strict resource limits and security.
"""
from typing import Any, Dict, Optional
import sys
import traceback
import io
from contextlib import redirect_stdout, redirect_stderr


class CodeRunner:
    """Execute code for supported languages (PoC).

    Currently supports 'python' by evaluating or executing code. Returns a
    result dict with stdout/stderr/result/error.
    """

    def run(self, language: str, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if language is None:
            language = "python"

        if language.lower() == "python":
            return self._run_python(code, context or {})

        return {"status": "error", "error": f"Unsupported language: {language}"}

    def _run_python(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        local_ns = dict(context)
        global_ns = {"__builtins__": __builtins__}

        try:
            # Try eval first for simple expressions
            try:
                compiled = compile(code, "<string>", "eval")
                with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                    value = eval(compiled, global_ns, local_ns)
                return {
                    "status": "ok",
                    "stdout": stdout_buf.getvalue(),
                    "stderr": stderr_buf.getvalue(),
                    "result": value,
                    "error": None,
                }
            except SyntaxError:
                # Fallback to exec
                compiled = compile(code, "<string>", "exec")
                with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
                    exec(compiled, global_ns, local_ns)
                return {
                    "status": "ok",
                    "stdout": stdout_buf.getvalue(),
                    "stderr": stderr_buf.getvalue(),
                    "result": None,
                    "error": None,
                }
        except Exception as exc:  # capture runtime errors
            tb = traceback.format_exc()
            return {
                "status": "error",
                "stdout": stdout_buf.getvalue(),
                "stderr": stderr_buf.getvalue(),
                "result": None,
                "error": str(exc),
                "traceback": tb,
            }
