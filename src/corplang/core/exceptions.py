"""Base exceptions from runtime"""
from copy import deepcopy
from enum import Enum, auto
from typing import Optional, List, Any, Dict

from src.corplang.compiler.nodes import ASTNode


class RuntimeErrorType(Enum):
    """Comprehensive error types for better error handling"""

    TYPE_ERROR = auto()
    REFERENCE_ERROR = auto()
    SYNTAX_ERROR = auto()
    SECURITY_ERROR = auto()
    RESOURCE_ERROR = auto()
    CONCURRENCY_ERROR = auto()
    MEMORY_ERROR = auto()
    IO_ERROR = auto()
    ASSERTION_ERROR = auto()
    RUNTIME_ERROR = auto()
    INTERNAL_RUNTIME = auto()
    ACCESS_CONTROL_ERROR = auto()


class CorpLangRuntimeError(Exception):
    """Enhanced runtime error with context and recovery suggestions"""

    # noinspection PyBroadException
    def __init__(
        self,
        message: str,
        error_type: RuntimeErrorType = RuntimeErrorType.TYPE_ERROR,
        node: Optional[ASTNode] = None,
        stack_trace: Optional[List[Dict[str, Any]]] = None,
        suggestions: Optional[List[str]] = None,
        recovery_possible: bool = False,
        file_name: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.node = node
        self.stack_trace = stack_trace or []
        self.suggestions = suggestions or []
        self.recovery_possible = recovery_possible
        self.file = file_name or (getattr(node, "file", None) if node is not None else None)
        # Formatted diagnostics string (optional)
        self.diagnostics: Optional[str] = None
        # frozen MP stack snapshot (optional)
        self.mp_stack: Optional[List[Dict[str, Any]]] = None
        # normalized MP-level exception object (optional)
        self.mp_exception: Optional[Any] = None
        if self.stack_trace and self.mp_stack is None:
            try:
                self.mp_stack = deepcopy(self.stack_trace)
            except Exception:
                try:
                    self.mp_stack = list(self.stack_trace)
                except Exception:
                    self.mp_stack = []

    def __str__(self) -> str:
        try:
            result = f"[{self.error_type.name}] {self.message}"
            file_name = self.file
            if not file_name and self.node:
                file_name = (
                    getattr(self.node, "file", None)
                    or getattr(self.node, "source_file", None)
                    or getattr(self.node, "filename", None)
                )
            if file_name:
                result += f" in {file_name}"
            if self.node:
                line = getattr(self.node, "line", None)
                if line:
                    result += f" at line {line}"
                    column = getattr(self.node, "column", None)
                    if column:
                        result += f", column {column}"

            if self.suggestions:
                result += "\nSuggestions:"
                for suggestion in self.suggestions:
                    try:
                        result += f"\n  - {suggestion}"
                    except Exception:
                        result += "\n  - <unrenderable suggestion>"

            return result
        except Exception:
            try:
                return f"[{getattr(self, 'error_type', '<error>')}] <error stringification failed>"
            except Exception:
                return "<error str() failed>"

    def printStackTrace(self, interpreter=None, workspace_root: Optional[str] = None):
        """Print the language-native stack trace using diagnostics.format_exception.

        Defaults to using the interpreter attached to the exception if available.
        """
        try:
            from src.corplang.tools.diagnostics import format_exception
            interp = interpreter or getattr(self, "interpreter", None)
            s = format_exception(self, executor=None, interpreter=interp, workspace_root=workspace_root)
            print(s)
        except Exception:
            # Best-effort fallback
            try:
                print(str(self))
            except Exception:
                pass

        return None


class ExecutionError(Exception):
    """Raised when execution fails."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        stack_trace: Optional[List[Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.stack_trace: List[Any] = stack_trace or []
        self.mp_stack: Optional[List[Dict[str, Any]]] = None
        self.diagnostics: Optional[str] = None

    def __str__(self) -> str:
        location = ""
        if self.line is not None:
            location = f" at line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"

        result = f"ExecutionError{location}: {self.message}"

        if self.stack_trace:
            result += "\nStack trace:\n" + "\n".join(
                f"  at {self._render_frame(f)}" for f in self.stack_trace
            )
        return result

    @staticmethod
    def _render_frame(frame: Any) -> str:
        """Render a stack frame."""
        if isinstance(frame, dict):
            file = frame.get("file", "<unknown>")
            line = frame.get("line")
            col = frame.get("column")
            return f"{file}:{line}" + (f":{col}" if col else "")
        return str(frame)


class ReturnException(Exception):
    """Returned exceptions"""
    def __init__(self, value: Any):
        self.value = value


class BreakException(Exception):
    """Exception raised by break statement to exit loops."""
    pass


class ContinueException(Exception):
    """Exception raised by continue statement to skip to the next iteration."""
    pass


class InternalRuntimeError(CorpLangRuntimeError):
    """Wraps host runtime errors (Python/IO/async) as a language-level internal error.

    Keeps original host exception in `cause` (but ensure diagnostics printed by the
    language are host-agnostic unless explicitly requested).
    """

    def __init__(self, message: str, cause: Optional[Exception] = None, node: Optional[ASTNode] = None, file_name: Optional[str] = None):
        super().__init__(message, RuntimeErrorType.INTERNAL_RUNTIME, node=node, file_name=file_name)
        self.cause = cause


class CorpLangRaisedException(Exception):
    """Wrapper for values raised by MP 'throw' statements."""

    def __init__(self, value: Any):
        self.value = value
        # Keep .message for backward compat with diagnostics
        try:
            from src.corplang.tools.diagnostics import safe_message
            self.message = value.message if hasattr(value, "message") else safe_message(value)
        except Exception:
            try:
                from src.corplang.tools.diagnostics import safe_message
                self.message = safe_message(value)
            except Exception:
                self.message = "<unrepresentable>"

    def __str__(self) -> str:
        return getattr(self, "message", "")
