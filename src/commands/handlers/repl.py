import sys
import tty
import termios
from typing import Optional
from pathlib import Path

from src.corplang.compiler import Lexer
from src.corplang.compiler.parser import Parser
from src.corplang.executor import execute
from src.corplang.tools.diagnostics import format_exception
from src.commands.utils.utils import Output, CLIResult, Colors, EnvManager


class REPL:
    """Interactive Read-Eval-Print Loop for Corplang."""

    # Node types that shouldn't produce output (declarations)
    SILENT_NODE_TYPES = {
        "FunctionDeclaration",
        "ClassDeclaration",
        "InterfaceDeclaration",
        "ImportStatement",
        "ExportStatement",
        "VarDeclaration",
        "ConstDeclaration",
        "TypeAlias",
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root
        self.history = []
        self.history_index = -1
        EnvManager.set_module_path(project_root)

    def run(self) -> CLIResult | None:
        """Start an interactive REPL session with multi-line support."""
        Output.section("Corplang Interactive Shell")
        Output.info("Type 'help' for commands, 'exit' to quit")
        Output.info("Press Enter twice to execute • ↑↓: history • ←→: navigate")
        Output.print()

        buffer = []
        while True:
            try:
                prompt = f"{Colors.GREEN}mf> {Colors.RESET}" if not buffer else f"{Colors.BLUE}  | {Colors.RESET}"
                line = self._read_line_with_history(prompt)

                # Check for special commands (only on the first line or empty buffer)
                if not buffer and line.strip():
                    cmd = line.strip().lower()

                    if cmd == "exit":
                        Output.info("Goodbye!")
                        return CLIResult(True, "REPL exit")
                    elif cmd == "help":
                        self._show_help()
                        continue
                    elif cmd.startswith("history"):
                        self._show_history()
                        continue
                    elif cmd.startswith("clear"):
                        self._clear_screen()
                        continue

                # Empty line: execute buffer or continue
                if not line.strip():
                    if buffer:
                        # Execute accumulated code
                        code = "\n".join(buffer)
                        self._execute_code(code)
                        self.history.append(code)
                        self.history_index = -1  # Reset history index
                        buffer = []
                        Output.print()  # Blank line after execution
                    continue

                # Add line to buffer
                buffer.append(line)
                self.history_index = -1  # Reset history index when adding new line

            except KeyboardInterrupt:
                Output.print()
                Output.info("Interrupted (Ctrl+C)")
                buffer = []
                self.history_index = -1
            except EOFError:
                Output.print()
                Output.info("Goodbye!")
                return CLIResult(True, "REPL exit")

    def _read_line_with_history(self, prompt: str) -> str:
        """Read a line with support for arrow keys (history ↑↓, cursor ←→)."""
        try:
            import sys
            if not sys.stdin.isatty():
                return input(prompt)
        except Exception:
            return input(prompt)

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            sys.stdout.write(prompt)
            sys.stdout.flush()

            line = ""
            cursor_pos = 0

            while True:
                ch = sys.stdin.read(1)

                # Arrow keys
                if ch == "\x1b":
                    next_ch = sys.stdin.read(1)
                    if next_ch == "[":
                        arrow = sys.stdin.read(1)

                        # Up arrow: previous history
                        if arrow == "A":
                            if self.history_index < len(self.history) - 1:
                                self.history_index += 1
                                line = self.history[-(self.history_index + 1)]
                                cursor_pos = len(line)
                                self._redraw_line(prompt, line, cursor_pos)

                        # Down arrow: next history
                        elif arrow == "B":
                            if self.history_index > 0:
                                self.history_index -= 1
                                line = self.history[-(self.history_index + 1)]
                                cursor_pos = len(line)
                                self._redraw_line(prompt, line, cursor_pos)
                            elif self.history_index == 0:
                                self.history_index = -1
                                line = ""
                                cursor_pos = 0
                                self._redraw_line(prompt, line, cursor_pos)

                        # Right arrow: move cursor right
                        elif arrow == "C":
                            if cursor_pos < len(line):
                                cursor_pos += 1
                                sys.stdout.write("\x1b[C")
                                sys.stdout.flush()

                        # Left arrow: move cursor left
                        elif arrow == "D":
                            if cursor_pos > 0:
                                cursor_pos -= 1
                                sys.stdout.write("\x1b[D")
                                sys.stdout.flush()

                # Backspace
                elif ch in ("\x7f", "\x08"):
                    if cursor_pos > 0:
                        line = line[:cursor_pos - 1] + line[cursor_pos:]
                        cursor_pos -= 1
                        self._redraw_line(prompt, line, cursor_pos)

                # Delete (forward delete)
                elif ch == "\x1b":
                    next_ch = sys.stdin.read(1)
                    if next_ch == "[":
                        arrow = sys.stdin.read(1)
                        if arrow == "3":
                            sys.stdin.read(1)  # consume ~
                            if cursor_pos < len(line):
                                line = line[:cursor_pos] + line[cursor_pos + 1:]
                                self._redraw_line(prompt, line, cursor_pos)

                # Enter
                elif ch == "\r" or ch == "\n":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return line

                # Ctrl+C
                elif ch == "\x03":
                    raise KeyboardInterrupt

                # Regular character
                elif ord(ch) >= 32:
                    line = line[:cursor_pos] + ch + line[cursor_pos:]
                    cursor_pos += 1
                    sys.stdout.write(ch)
                    # Redraw rest of line if not at end
                    if cursor_pos < len(line):
                        sys.stdout.write(line[cursor_pos:])
                        sys.stdout.write("\x1b[D" * (len(line) - cursor_pos))
                    sys.stdout.flush()

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    @staticmethod
    def _redraw_line(prompt: str, line: str, cursor_pos: int):
        """Redraw the current line with proper cursor positioning."""
        sys.stdout.write("\r" + prompt + line + " " * 20)  # Extra spaces to clear
        sys.stdout.write("\r" + prompt + line)
        if cursor_pos < len(line):
            sys.stdout.write("\x1b[D" * (len(line) - cursor_pos))
        sys.stdout.flush()

    def _execute_code(self, code: str):
        """Parse and execute code, displaying results (filtered)."""
        try:
            # Disable UI output from parser
            import os
            old_debug = os.environ.get("CORPLANG_DEBUG")
            os.environ["CORPLANG_DEBUG"] = "0"

            lexer = Lexer(code)
            parser = Parser(lexer.tokenize(), "<repl>")
            parser.compiler_view = False  # Disable verbose logging

            ast = parser.parse()

            if old_debug is not None:
                os.environ["CORPLANG_DEBUG"] = old_debug
            else:
                os.environ.pop("CORPLANG_DEBUG", None)

            if not ast or not ast.statements:
                return

            result = execute(ast)
            
            # Only print non-None results that aren't silent node types
            if result is not None:
                result_type = type(result).__name__
                
                # Skip silent declarations
                if result_type in self.SILENT_NODE_TYPES:
                    return
                
                # Skip AST nodes entirely (print only values)
                if hasattr(result, "line") and hasattr(result, "column"):
                    return
                
                Output.print(f"{Colors.CYAN}{result}{Colors.RESET}")

        except SyntaxError as e:
            Output.error(f"Syntax: {e}")
        except Exception as e:
            error_output = format_exception(e)
            Output.error(f"Error:\n{error_output}")

    @staticmethod
    def _show_help():
        """Display help message."""
        Output.print(f"""
{Colors.BOLD}Available Commands:{Colors.RESET}
  help           - Show this message
  history        - Show command history
  clear          - Clear screen
  exit           - Exit REPL

{Colors.BOLD}Input Mode:{Colors.RESET}
  • Type code normally and press Enter twice to execute
  • Multi-line statements are supported
  • Empty line triggers execution

{Colors.BOLD}Examples:{Colors.RESET}
  mf> 1 + 2
  (press Enter twice)
  3

  mf> intent greet() {{
    |   return "Hello"
    | }}
  (press Enter twice - function defined, no output)
""")

    def _show_history(self):
        """Display command history."""
        if not self.history:
            Output.info("No history")
            return

        Output.print(f"\n{Colors.BOLD}History ({len(self.history)} commands):{Colors.RESET}")
        for i, cmd in enumerate(self.history, 1):
            # Show first line of multi-line commands
            first_line = cmd.split("\n")[0]
            Output.print(f"  {i:3}. {first_line}")
        Output.print()

    @staticmethod
    def _clear_screen():
        """Clear the terminal screen."""
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()


# noinspection PyUnusedLocal
def handle_repl(args) -> CLIResult:
    """CLI handler for REPL command."""
    from src.commands.config import CorplangConfig

    project_root = CorplangConfig.get_project_root()
    repl = REPL(project_root)
    return repl.run()
