import sys
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import time


@dataclass
class CLIResult:
    success: bool
    message: str = ""
    exit_code: int = 0


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @staticmethod
    def disable_if_not_tty():
        if not sys.stdout.isatty():
            for attr in dir(Colors):
                if not attr.startswith("_"):
                    setattr(Colors, attr, "")


class Output:
    @staticmethod
    def info(msg: str):
        print(f"{Colors.CYAN}ℹ {Colors.RESET}{msg}")

    @staticmethod
    def success(msg: str):
        print(f"{Colors.GREEN}✓ {Colors.RESET}{msg}")

    @staticmethod
    def warning(msg: str):
        print(f"{Colors.YELLOW}⚠ {Colors.RESET}{msg}", file=sys.stderr)

    @staticmethod
    def error(msg: str):
        print(f"{Colors.RED}✗ {Colors.RESET}{msg}", file=sys.stderr)

    @staticmethod
    def debug(msg: str, verbose: bool = False):
        if verbose:
            print(f"{Colors.GRAY}◆ {Colors.RESET}{msg}", file=sys.stderr)

    @staticmethod
    def section(title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")

    @staticmethod
    def print(msg: str = ""):
        print(msg)


class FileValidator:
    @staticmethod
    def validate_corplang_file(file_path: str) -> tuple[bool, str]:
        """Validate that file exists and is a .mp file."""
        path = Path(file_path)

        if not path.exists():
            return False, f"File not found: {file_path}"

        if not file_path.endswith((".mp", ".mf")):
            return False, f"Invalid extension. Expected .mp or .mf, got {path.suffix}"

        if not path.is_file():
            return False, f"Path is not a file: {file_path}"

        return True, ""

    @staticmethod
    def find_corplang_files(directory: str, recursive: bool = True) -> list[Path]:
        """Find all .mp and .mf files in directory."""
        dir_path = Path(directory)
        if not dir_path.exists():
            return []

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        files = []
        for ext in ["*.mp", "*.mf"]:
            files.extend(dir_path.glob(f"{pattern}.{ext[2:]}"))

        return sorted(set(files))


class PathResolver:
    @staticmethod
    def resolve_relative_path(file_path: str, base_dir: Optional[Path] = None) -> Path:
        """Resolve path relative to base_dir or current directory."""
        if not base_dir:
            base_dir = Path.cwd()

        path = Path(file_path)
        if path.is_absolute():
            return path

        resolved = (base_dir / path).resolve()
        return resolved

    @staticmethod
    def get_relative_to_cwd(file_path: Path) -> Path:
        """Get path relative to current working directory."""
        try:
            return file_path.relative_to(Path.cwd())
        except ValueError:
            return file_path


class Timer:
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()

    def elapsed(self) -> float:
        if self.end_time is None:
            return time.time() - self.start_time if self.start_time else 0
        return self.end_time - self.start_time

    def report(self):
        elapsed = self.elapsed()
        if elapsed < 1:
            msg = f"{elapsed * 1000:.1f}ms"
        else:
            msg = f"{elapsed:.2f}s"
        Output.info(f"{self.name} completed in {msg}")


class EnvManager:
    @staticmethod
    def get_corplang_debug() -> bool:
        return os.environ.get("CORPLANG_DEBUG", "").lower() in ("1", "true", "yes")

    @staticmethod
    def get_corplang_strict() -> bool:
        return os.environ.get("CORPLANG_STRICT", "").lower() in ("1", "true", "yes")

    @staticmethod
    def get_corplang_home() -> Path:
        custom = os.environ.get("CORPLANG_HOME")
        if custom:
            return Path(custom)
        return Path.home() / ".corplang"

    @staticmethod
    def set_module_path(project_root: Optional[Path] = None):
        """Add module search paths to sys.path."""
        from src.commands.config import CorplangConfig

        paths = CorplangConfig.resolve_module_search_paths(project_root)
        for path in paths:
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)


def safe_load_file(file_path: str) -> Optional[str]:
    """Safely load file contents with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        Output.error(f"File is not UTF-8 encoded: {file_path}")
        return None
    except IOError as e:
        Output.error(f"Cannot read file: {e}")
        return None


def safe_write_file(file_path: str, content: str) -> bool:
    """Safely write file contents with error handling."""
    try:
        Path(file_path).parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except IOError as e:
        Output.error(f"Cannot write file: {e}")
        return False


class Spinner:
    """Animated spinner for long operations."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str = "Processing..."):
        self.message = message
        self.index = 0
        self.running = False

    def start(self):
        """Start spinner in current thread (non-blocking)."""
        if not sys.stdout.isatty():
            Output.info(self.message)
            return

        self.running = True
        while self.running:
            frame = self.FRAMES[self.index % len(self.FRAMES)]
            sys.stdout.write(f"\r{frame} {self.message}")
            sys.stdout.flush()
            self.index += 1
            time.sleep(0.1)

    def stop(self, success: bool = True):
        """Stop spinner with result indicator."""
        self.running = False
        if not sys.stdout.isatty():
            return

        symbol = "✓" if success else "✗"
        sys.stdout.write(f"\r{symbol} {self.message}\n")
        sys.stdout.flush()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()


class SelectMenu:
    """Interactive selection menu with arrow key navigation."""

    def __init__(self, options: list[str], title: str = "Select an option:"):
        self.options = options
        self.title = title
        self.selected = 0

    def show(self) -> Optional[str]:
        """Display menu and return selected option."""
        if not self.options:
            return None

        try:
            import tty
            import termios
            has_tty = sys.stdin.isatty()
        except ImportError:
            has_tty = False

        if not has_tty:
            return self._show_numbered()

        return self._show_interactive()

    def _show_numbered(self) -> Optional[str]:
        """Fallback numbered menu."""
        Output.print(f"\n{Colors.CYAN}{self.title}{Colors.RESET}")
        for i, opt in enumerate(self.options, 1):
            Output.print(f"  {i}. {opt}")

        while True:
            try:
                choice = input(f"\n{Colors.GREEN}Enter (1-{len(self.options)}) or 'q': {Colors.RESET}")
                if choice.lower() in ('q', ''):
                    return None
                num = int(choice)
                if 1 <= num <= len(self.options):
                    return self.options[num - 1]
            except (ValueError, KeyboardInterrupt, EOFError):
                return None

    def _show_interactive(self) -> Optional[str]:
        """Arrow key navigation."""
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            self._render(initial=True)

            while True:
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # Arrow keys
                    sys.stdin.read(1)  # Skip '['
                    arrow = sys.stdin.read(1)
                    if arrow == 'A' and self.selected > 0:
                        self.selected -= 1
                        self._render()
                    elif arrow == 'B' and self.selected < len(self.options) - 1:
                        self.selected += 1
                        self._render()
                elif ch in ('\r', '\n'):
                    self._clear_menu()
                    return self.options[self.selected]
                elif ch in ('q', 'Q', '\x03'):  # q or Ctrl+C
                    self._clear_menu()
                    return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _render(self, initial: bool = False):
        """Render menu with current selection."""
        if initial:
            sys.stdout.write(f"\n{Colors.CYAN}{self.title}{Colors.RESET}\n\n")
        else:
            # Move cursor up to redraw menu items
            lines = len(self.options) + 1  # options + help line
            sys.stdout.write(f'\033[{lines}A\r')  # Move up and to start of line
        
        for i, opt in enumerate(self.options):
            marker = "►" if i == self.selected else " "
            color = Colors.GREEN if i == self.selected else ""
            reset = Colors.RESET if i == self.selected else ""
            sys.stdout.write(f"\r\033[K  {marker} {color}{opt}{reset}\n")  # Clear line, write, newline
        sys.stdout.write(f"\r\033[K\n{Colors.DIM}↑↓: Navigate | Enter: Select | q: Cancel{Colors.RESET}")
        sys.stdout.flush()
    
    def _clear_menu(self):
        """Clear menu lines."""
        lines = len(self.options) + 1
        sys.stdout.write(f'\033[{lines}A')  # Move up
        for _ in range(lines + 1):
            sys.stdout.write('\033[K\n')  # Clear each line
        sys.stdout.write(f'\033[{lines + 1}A')  # Move back up
        sys.stdout.flush()


class ProgressBar:
    """Simple progress bar for downloads and long operations."""

    def __init__(self, total: int, prefix: str = "", suffix: str = ""):
        self.total = max(total, 1)
        self.current = 0
        self.prefix = prefix
        self.suffix = suffix

    def update(self, amount: int = 1):
        """Update progress."""
        self.current = min(self.current + amount, self.total)
        if not sys.stdout.isatty():
            return

        percent = int((self.current / self.total) * 100)
        filled = int((self.current / self.total) * 40)
        bar = "█" * filled + "░" * (40 - filled)

        sys.stdout.write(f"\r{self.prefix} {bar} {percent}% {self.suffix}")
        sys.stdout.flush()

        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
