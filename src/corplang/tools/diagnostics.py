import os
import sys
import traceback
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FrameInfo:
    file_path: str
    rel_path: str
    line: Optional[int]
    column: Optional[int]
    function: Optional[str]
    node: Optional[str]
    code: Optional[str]
    variables: Dict[str, Any]
    memory_estimate: Optional[int]


def _safe_repr(v: Any) -> str:
    try:
        return repr(v)
    except Exception:
        try:
            return str(v)
        except Exception:
            return "<unrepresentable>"


def safe_message(v: Any) -> str:
    """Return a human-friendly message for an exception or value without raising.

    Prefer `.message` when available; fallback to safe repr.
    """
    try:
        # Prefer user-provided message
        if hasattr(v, "message"):
            m = getattr(v, "message")
            try:
                return str(m)
            except Exception:
                return _safe_repr(m)
    except Exception:
        pass
    return _safe_repr(v)


def _read_source_snippet(
    file_path: Optional[str], line: Optional[int], context: int = 0
) -> Optional[str]:
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if line is None:
            return "".join(lines).strip()
        idx = max(0, line - 1)
        if 0 <= idx < len(lines):
            return lines[idx].rstrip("\n")
        return None
    except Exception:
        return None


def _estimate_memory(v: Any) -> Optional[int]:
    try:
        return sys.getsizeof(v)
    except Exception:
        return None


def _clean_message(v: Any, max_len: int = 200) -> str:
    """Return a cleaned, single-line message for display."""
    try:
        s = safe_message(v)
    except Exception:
        s = _safe_repr(v)
    if s is None:
        return ""
    s = str(s).replace("\n", " ").strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1].strip()
    if len(s) > max_len:
        s = s[: max_len - 3].rstrip() + "..."
    return s


def _summarize_variables(vars_map: Dict[str, Any], max_items: int = 3, hide_functions: bool = True) -> str:
    """Create a compact single-line summary of variables map."""
    try:
        items = []
        for k, v in vars_map.items():
            if k.startswith("__"):
                continue
            v_type = v.get("type") if isinstance(v, dict) else type(v).__name__
            v_val = v.get("value") if isinstance(v, dict) else v
            if hide_functions and (str(v_type).lower() == "function" or "<function" in str(v_val)):
                continue
            items.append((k, v_val, v_type))
        if not items:
            return ""
        shown = items[:max_items]
        parts = [f"{k}={_safe_repr(val)} ({tp})" for k, val, tp in shown]
        if len(items) > len(shown):
            parts.append(f"+{len(items) - len(shown)} more")
        return "; ".join(parts)
    except Exception:
        return ""


def classify_exception(ex: Exception) -> str:
    try:
        from src.corplang.core.exceptions import ExecutionError
    except Exception:
        ExecutionError = None

    try:
        from src.corplang.core.exceptions import CorpLangRuntimeError
    except Exception:
        CorpLangRuntimeError = None

    if ExecutionError and isinstance(ex, ExecutionError):
        m = safe_message(ex).lower()
        if "undefined variable" in m or "not found" in m:
            return "ReferenceError"
        if "division by zero" in m:
            return "RuntimeError"
        if "type" in m and "mismatch" in m:
            return "TypeError"
        if "invalid assignment" in m or "cannot assign" in m:
            return "SyntaxError"
        return "ExecutionError"

    if CorpLangRuntimeError and isinstance(ex, CorpLangRuntimeError):
        return getattr(ex, "error_type").name if hasattr(ex, "error_type") else "RuntimeError"

    if isinstance(ex, FileNotFoundError):
        return "FileNotFoundError"
    if isinstance(ex, (OSError, IOError)):
        return "IOError"
    if isinstance(ex, asyncio.TimeoutError):
        return "TimeoutError"
    if isinstance(ex, asyncio.CancelledError):
        return "ConcurrencyError"
    if isinstance(ex, MemoryError):
        return "MemoryError"
    if isinstance(ex, AssertionError):
        return "AssertionError"
    return type(ex).__name__

def _build_mp_frames_from_executor(
    ex: Exception, executor=None, workspace_root: Optional[str] = None
) -> List[FrameInfo]:
    frames: List[FrameInfo] = []
    current_module = getattr(executor, "current_module_path", None) if executor else None

    stack_entries = []
    if hasattr(ex, "stack_trace") and getattr(ex, "stack_trace"):
        stack_entries = list(getattr(ex, "stack_trace"))
    else:
        line = getattr(ex, "line", None)
        column = getattr(ex, "column", None)
        if line is not None:
            stack_entries = [f"line {line}, column {column}" if column else f"line {line}"]

    for entry in stack_entries:
        if isinstance(entry, dict):
            origin_file = entry.get("origin_file") or entry.get("file")
            file_path = origin_file or current_module or getattr(executor, "runtime_source_root", None)
            exec_file = entry.get("exec_file") or current_module or getattr(executor, "runtime_source_root", None)
            line = entry.get("line")
            col = entry.get("column")
            exec_locals = entry.get("locals") or entry.get("variables") or {}
            variables = {
                name: {"value": _safe_repr(val), "type": type(val).__name__, "memory_estimate": _estimate_memory(val)}
                for name, val in list(exec_locals.items())[:10]
            }
            rel_path = os.path.relpath(file_path, workspace_root) if file_path and workspace_root else (file_path or "<unknown>")
            code_line = _read_source_snippet(file_path, line)
            frame = FrameInfo(
                file_path=file_path or "<unknown>",
                rel_path=rel_path,
                line=line,
                column=col,
                function=entry.get("function") or entry.get("function_name"),
                node=entry.get("node"),
                code=code_line,
                variables=variables,
                memory_estimate=None,
            )
            if exec_file and exec_file != file_path:
                frame.variables["__exec_file__"] = {"value": exec_file, "type": "string", "memory_estimate": None}
            frames.append(frame)
            continue

        line, col = None, None
        try:
            parts = entry.replace(",", "").split()
            if "line" in parts:
                i = parts.index("line")
                if i + 1 < len(parts):
                    line = int(parts[i + 1])
            if "column" in parts:
                i = parts.index("column")
                if i + 1 < len(parts):
                    col = int(parts[i + 1])
        except Exception:
            pass

        file_path = current_module or getattr(executor, "runtime_source_root", None) or None
        rel_path = os.path.relpath(file_path, workspace_root) if file_path and workspace_root else (file_path or "<unknown>")
        code_line = _read_source_snippet(file_path, line)

        variables = {}
        try:
            if executor and hasattr(executor, "current_scope") and getattr(executor, "current_scope"):
                scope_vars = getattr(executor.current_scope, "variables", {})
                variables = {
                    name: {"value": _safe_repr(val), "type": type(val).__name__, "memory_estimate": _estimate_memory(val)}
                    for name, val in list(scope_vars.items())[:10]
                }
        except Exception:
            pass

        frames.append(FrameInfo(
            file_path=file_path or "<unknown>",
            rel_path=rel_path,
            line=line,
            column=col,
            function=None,
            node=None,
            code=code_line,
            variables=variables,
            memory_estimate=None,
        ))

    return frames


def _build_mp_frames_from_interpreter(
    ex: Exception, interpreter=None, workspace_root: Optional[str] = None
) -> List[FrameInfo]:
    frames: List[FrameInfo] = []
    if not interpreter or not hasattr(interpreter, "call_stack"):
        return frames

    for frame in list(getattr(interpreter, "call_stack")):
        try:
            file_path = frame.get("origin_file") or frame.get("file") or frame.get("filename") or frame.get("path")
            line = frame.get("origin_line") if frame.get("origin_line") is not None else frame.get("line")
            col = frame.get("column")
            function = frame.get("name") or frame.get("function") or "<module>"
            rel_path = os.path.relpath(file_path, workspace_root) if file_path and workspace_root else (file_path or "<unknown>")
            code_line = _read_source_snippet(file_path, line)

            locals_map = frame.get("locals") or frame.get("variables") or {}
            variables = {
                name: {"value": _safe_repr(val), "type": type(val).__name__, "memory_estimate": _estimate_memory(val)}
                for name, val in list(locals_map.items())[:10]
            }

            frame_info = FrameInfo(
                file_path=file_path,
                rel_path=rel_path,
                line=line,
                column=col,
                function=function,
                node=frame.get("node"),
                code=code_line,
                variables=variables,
                memory_estimate=None,
            )
            if frame.get("exec_file") and frame.get("exec_file") != file_path:
                frame_info.variables["__exec_file__"] = {"value": frame.get("exec_file"), "type": "string", "memory_estimate": None}
            frames.append(frame_info)
        except Exception:
            continue
    return frames


def format_exception(
    ex: Exception, executor=None, interpreter=None, workspace_root: Optional[str] = None
) -> str:
    """Format an exception per the user's spec.

    Returns a string structured with Error line, StackTrace only with .mp frames, Root Cause, Suggestions and optional Internal Interpreter Diagnostics.
    """
    # First, classify exception
    err_type = classify_exception(ex)
    # Use message safely
    msg = safe_message(ex)

    # Prefer an explicit frozen mp stack attached to the exception object
    frames = []
    try:
        # support 'mpStack' (from wrap_as_mp_exception) or 'mp_stack' (from exceptions)
        frozen = None
        if hasattr(ex, "mpStack") and getattr(ex, "mpStack"):
            frozen = getattr(ex, "mpStack")
        elif hasattr(ex, "mp_stack") and getattr(ex, "mp_stack"):
            frozen = getattr(ex, "mp_stack")
        if frozen:
            # Build FrameInfo objects from the frozen list if they are dicts
            for entry in frozen:
                if isinstance(entry, dict):
                    file_path = entry.get("file")
                    # prefer the node-origin line if present
                    line = entry.get("origin_line") if entry.get("origin_line") is not None else entry.get("line")
                    col = entry.get("column")
                    func = entry.get("function") or "<module>"
                    rel_path = (
                        os.path.relpath(file_path, workspace_root)
                        if (file_path and workspace_root)
                        else (file_path or "<unknown>")
                    )
                    code_line = _read_source_snippet(file_path, line)
                    variables = {}
                    exec_locals = entry.get("locals") or {}
                    for name, val in list(exec_locals.items())[:10]:
                        variables[name] = {
                            "value": _safe_repr(val),
                            "type": type(val).__name__,
                            "memory_estimate": _estimate_memory(val),
                        }
                    node_name = entry.get("node") or entry.get("type") or None
                    frames.append(
                        FrameInfo(
                            file_path=file_path or "<unknown>",
                            rel_path=rel_path,
                            line=line,
                            column=col,
                            function=func,
                            node=node_name,
                            code=code_line,
                            variables=variables,
                            memory_estimate=None,
                        )
                    )
            # If we have reconstructed frames, we are done
            if frames:
                pass
    except Exception:
        frames = []

    # If no frozen frames available, fallback to interpreter or executor supplied frames
    if not frames:
        if interpreter and hasattr(interpreter, "call_stack") and interpreter.call_stack:
            frames = _build_mp_frames_from_interpreter(ex, interpreter, workspace_root)
        else:
            frames = _build_mp_frames_from_executor(ex, executor, workspace_root)

    # Compose stack trace string
    stack_lines: List[str] = []
    cleaned_header = _clean_message(ex)
    header_msg = cleaned_header if cleaned_header else msg
    # Present as a small block: Error, Message and an optional Location (if top frame available)
    stack_lines.append(f"Error<{err_type}>")
    stack_lines.append(f"Message: {header_msg}")
    # Include a short location line from the most recent MP frame for quick scanning
    try:
        if frames:
            top = frames[-1]
            loc = f"{top.rel_path}:{top.line}" if top.line is not None else f"{top.rel_path}"
            fn = f" in {top.function}" if getattr(top, "function", None) else ""
            stack_lines.append(f"Location: {loc}{fn}")
    except Exception:
        pass

    stack_lines.append("")
    stack_lines.append("StackTrace (.mp):")

    if not frames:
        stack_lines.append("  <no .mp frames available>")
    else:
        # Print in Java-like order: most recent frame first
        first = True
        for f in reversed(frames):
            func = f.function or "<module>"
            called_from = None
            try:
                cf = f.variables.get("__exec_file__") if isinstance(f.variables, dict) else None
                if cf and isinstance(cf, dict):
                    called_from = cf.get("value")
            except Exception:
                called_from = None
            frame_line = (
                f"  at {f.rel_path}:{f.line}  in {func}"
                if f.line
                else f"  at {f.rel_path}  in {func}"
            )
            # Mark the most recent frame as the likely origin of the throw
            if first:
                frame_line += "  <-- origem do erro"
                first = False
            if called_from and called_from != f.file_path:
                try:
                    called_rel = (
                        os.path.relpath(called_from, workspace_root)
                        if (called_from and workspace_root)
                        else called_from
                    )
                    frame_line += f"  (called from {called_rel})"
                except Exception:
                    frame_line += f"  (called from {called_from})"
            stack_lines.append(frame_line)
            if f.code:
                stack_lines.append(f"    codeblock: {f.code}")
            if f.variables:
                # Show a compact variables map (prefer user variables, hide functions)
                vars_summary = _summarize_variables(f.variables, max_items=3, hide_functions=True)
                if vars_summary:
                    stack_lines.append(f"    variáveis: {{{vars_summary}}}")
            if f.memory_estimate is not None:
                stack_lines.append(f"    memória estimada (bytes): {f.memory_estimate}")

    # Root cause: attempt to provide the most likely reason
    root_lines: List[str] = [""]
    root_lines.append("Root Cause:")
    # Determine root cause location — prefer the most relevant frame: scan most-recent-first for the most precise frame
    cause = getattr(ex, "cause", None)
    chosen = None
    try:
        for f in reversed(frames):
            # Prefer a frame that has an explicit line and either: explicit column, non-module function, code snippet, or a concrete node type
            if (
                f.line is not None
                and (
                    f.column is not None
                    or (f.function and f.function != "<module>")
                    or (f.code and str(f.code).strip())
                    or (f.node and f.node != "<module>" and f.node != "Program")
                )
            ):
                chosen = f
                break
        # fallback to the most recent frame if none matched
        if chosen is None and frames:
            chosen = frames[-1]
    except Exception:
        chosen = frames[-1] if frames else None

    if chosen is not None:
        root_lines.append(f"  Possible error at {chosen.rel_path}:{chosen.line}")
        try:
            cleaned = _clean_message(ex)
            if cleaned:
                root_lines.append(f"  Message: {cleaned}")
        except Exception:
            pass
        # If the chosen frame lacks a precise line, but includes a code snippet, show it to aid debugging
        try:
            if chosen.line is None and chosen.code:
                code_snip = str(chosen.code).strip()
                if code_snip:
                    root_lines.append(f"  Code: {code_snip}")
        except Exception:
            pass
        if "undefined variable" in msg.lower() or "not found" in msg.lower():
            root_lines.append("  Note: undefined reference / missing symbol")
        elif "division by zero" in msg.lower():
            root_lines.append("  Note: attempted division by zero (check denominators)")
        elif "type mismatch" in msg.lower() or "type" in msg.lower():
            root_lines.append("  Note: type mismatch; check variable types or generics")
    else:
        # No MP frames: still include direct message and cause information when possible
        try:
            cleaned = _clean_message(ex)
            root_lines.append(f"  {cleaned if cleaned else '<no additional message available>'}")
        except Exception:
            root_lines.append("  <no additional message available>")

    # If there is an underlying host cause, add a short one-line summary to help tracing
    if cause is not None:
        try:
            cause_msg = _clean_message(cause)
        except Exception:
            cause_msg = "<unrepresentable>"
        try:
            root_lines.append(f"  Caused by: {type(cause).__name__} — {cause_msg}")
        except Exception:
            root_lines.append(f"  Caused by: {cause_msg}")

    # Suggestions
    suggestions: List[str] = [""]
    suggestions.append("Suggestions:")
    if "undefined variable" in msg.lower():
        suggestions.append(
            "  - Ensure variable is defined before use; check variable name spelling and scope."
        )
        suggestions.append(
            "  - If referencing a module symbol, ensure the module is imported and the name exported."
        )
    if "division by zero" in msg.lower():
        suggestions.append(
            "  - Guard division operations, check denominators are non-zero, or use safe math helpers."
        )
    if "type mismatch" in msg.lower() or "does not accept null" in msg.lower():
        suggestions.append(
            "  - Check parameter types and Optional annotations; ensure correct types are passed."
        )
    if "invalid assignment" in msg.lower() or "cannot assign" in msg.lower():
        suggestions.append(
            "  - Assignment target invalid; confirm assignment target is a variable name or property."
        )
    if not suggestions[1:] or len(suggestions) == 2:
        suggestions.append(
            "  - Inspect variables/stack trace above to locate the cause and adjust the code accordingly."
        )

    # Build final message
    out_lines = stack_lines + root_lines + suggestions

    # Internal Interpreter Diagnostics (hidden by default)
    internal_lines = ["", "Internal Interpreter Diagnostics:"]
    was_internal_shown = False
    try:
        # Only include host trace when interpreter explicitly asks for internal diagnostics
        interp = interpreter
        show_internal = bool(getattr(interp, "show_internal_diagnostics", False)) if interp is not None else False
        if show_internal:
            internal_lines.append("")
            internal_lines.append("Host traceback (internal):")
            tb = "".join(traceback.format_exception(type(ex), ex, ex.__traceback__))
            internal_lines.append(tb)
            was_internal_shown = True
    except Exception:
        was_internal_shown = False

    if was_internal_shown:
        out_lines += internal_lines


    return "\n".join(out_lines)


def wrap_as_mp_exception(ex: Exception, executor=None, interpreter=None, workspace_root: Optional[str] = None):
    """Wrap a Python exception into a user-level MP exception object."""

    err_type = classify_exception(ex)
    payload = getattr(ex, "message", ex)
    payload_type = None
    try:
        from src.corplang.core.exceptions import CorpLangRaisedException
        if isinstance(ex, CorpLangRaisedException) and hasattr(ex, "message"):
            payload = ex.message
    except Exception:
        pass

    try:
        if hasattr(payload, "class_obj") and getattr(payload, "class_obj"):
            payload_type = getattr(getattr(payload, "class_obj"), "name", None)
    except Exception:
        pass

    if payload_type:
        err_type = payload_type

    cause = getattr(ex, "cause", None) if ex else None

    if cause:
        if isinstance(cause, FileNotFoundError):
            err_type = "FileNotFoundError"
        elif isinstance(cause, (OSError, IOError)):
            err_type = "IOError"
        elif isinstance(cause, asyncio.TimeoutError):
            err_type = "TimeoutError"
        elif isinstance(cause, asyncio.CancelledError):
            err_type = "ConcurrencyError"
        elif isinstance(cause, MemoryError):
            err_type = "MemoryError"

    msg = safe_message(payload)

    payload_class_name = None
    try:
        if hasattr(payload, "class_obj") and getattr(payload, "class_obj"):
            payload_class_name = getattr(getattr(payload, "class_obj"), "name", None)
    except Exception:
        pass

    frozen = []
    if hasattr(ex, "mp_stack") and getattr(ex, "mp_stack"):
        frozen = list(getattr(ex, "mp_stack"))
    else:
        try:
            if executor and getattr(executor, "call_stack", None):
                frozen = list(getattr(executor, "call_stack"))
            elif interpreter and getattr(interpreter, "call_stack", None):
                frozen = list(getattr(interpreter, "call_stack"))
        except Exception:
            pass

    internal = None
    try:
        internal = format_exception(ex, executor=executor, interpreter=interpreter, workspace_root=workspace_root)
    except Exception:
        pass

    class MPExceptionObj:
        def __init__(self, type_name, message, mp_stack, metadata, diagnostics, original_ex):
            self.type = type_name
            self.message = message
            self.mpStack = mp_stack
            self.metadata = metadata
            self.internalDiagnostics = diagnostics
            self._original_ex = original_ex
            if payload_class_name:
                self.payload_class_name = payload_class_name

        def printStackTrace(self):
            s = format_exception(self._original_ex, executor=executor, interpreter=interpreter, workspace_root=workspace_root)
            print(s)

        def printInternalDiagnostics(self):
            print(self.internalDiagnostics or "<no internal diagnostics available>")

        def __repr__(self):
            return f"MPException(type={self.type}, message={self.message})"

    if payload and not isinstance(payload, (str, int, float, bool, list, tuple, dict)):
        if not hasattr(payload, "mpStack"):
            try:
                setattr(payload, "mpStack", frozen)
            except Exception:
                pass
        if not hasattr(payload, "internalDiagnostics"):
            try:
                setattr(payload, "internalDiagnostics", internal)
            except Exception:
                pass
        return payload

    error_category = None
    cause_ex = getattr(ex, "cause", None) or ex
    if isinstance(cause_ex, FileNotFoundError):
        error_category = "IO_ERROR"
    elif isinstance(cause_ex, (OSError, IOError)):
        error_category = "IO_ERROR"
    elif isinstance(cause_ex, asyncio.TimeoutError):
        error_category = "CONCURRENCY_ERROR"
    elif isinstance(cause_ex, asyncio.CancelledError):
        error_category = "CONCURRENCY_ERROR"
    elif isinstance(cause_ex, MemoryError):
        error_category = "MEMORY_ERROR"
    elif isinstance(cause_ex, AssertionError):
        error_category = "ASSERTION_ERROR"

    obj = MPExceptionObj(err_type, msg, frozen, {"error_category": error_category} if error_category else {}, internal, ex)

    def print_stack_trace():
        s = format_exception(ex, executor=executor, interpreter=interpreter, workspace_root=workspace_root)
        print(s)

    def print_internal():
        print(internal or "<no internal diagnostics available>")

    setattr(obj, "printStackTrace", print_stack_trace)
    setattr(obj, "printInternalDiagnostics", print_internal)

    return obj
