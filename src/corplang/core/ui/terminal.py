import time
import sys
import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass
import yaml
import os


@dataclass
class UITheme:
    """ANSI color theme definition for terminal UI."""
    name: str
    primary: str
    secondary: str
    success: str
    warning: str
    error: str
    info: str
    dim: str
    bold: str = "\033[1m"
    reset: str = "\033[0m"


class TerminalUI:
    """Lightweight animated and colored terminal UI for logs and build steps."""

    DEFAULT_THEMES = {
        "uv": UITheme(
            "uv",
            "\033[38;5;147m",
            "\033[38;5;75m",
            "\033[38;5;84m",
            "\033[38;5;215m",
            "\033[38;5;203m",
            "\033[38;5;117m",
            "\033[38;5;244m",
        ),
        "dark": UITheme(
            "dark",
            "\033[36m",
            "\033[34m",
            "\033[32m",
            "\033[33m",
            "\033[31m",
            "\033[37m",
            "\033[90m",
        ),
    }

    def __init__(self, config_path: str = "config.yml"):
        """Initialize UI settings, theme, and animation behavior."""
        cfg = self._load_config(config_path).get("ui", {})
        self.theme = self.DEFAULT_THEMES.get(cfg.get("theme", "uv"), self.DEFAULT_THEMES["uv"])
        self.delay = cfg.get("animation_speed", 0.02)
        self.enabled = cfg.get("enabled", True)
        self._lock = threading.Lock()

    @staticmethod
    def _load_config(path: str) -> Dict[str, Any]:
        """Load YAML configuration file if it exists."""
        if os.path.exists(path):
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _print(self, text: str, end: str = "\n"):
        """Print text immediately if UI output is enabled."""
        if self.enabled:
            sys.stdout.write(text + end)
            sys.stdout.flush()

    def _animate(self, text: str, end: str = "\n"):
        """Print text with a slow character-by-character animation."""
        if not self.enabled:
            return self._print(text, end)

        for c in text:
            sys.stdout.write(c)
            sys.stdout.flush()
            time.sleep(self.delay)
        sys.stdout.write(end)
        sys.stdout.flush()
        return None

    def log(self, message: str, level: str = "info", prefix: str = ""):
        """Display a colored log line with a level label."""
        color = getattr(self.theme, level, self.theme.info)
        label = level.upper().center(10)
        self._print(f"{self.theme.dim}{prefix}{self.theme.reset} {color}{label}{self.theme.reset} {message}")

    def status(self, action: str, target: str, color: Optional[str] = None, animate: bool = False):
        """Show a build-style status line (UV-like)."""
        color = color or self.theme.primary
        line = f"{self.theme.bold}{color}{action.lower():>12}{self.theme.reset} {target}"
        (self._animate if animate else self._print)(line)

    def progress_bar(self, current: int, total: int, prefix: str = "", length: int = 40):
        """Render an in-place progress bar."""
        if not self.enabled:
            return

        ratio = current / total
        filled = int(length * ratio)
        bar = "█" * filled + "░" * (length - filled)
        sys.stdout.write(
            f"\r{self.theme.dim}{prefix}{self.theme.reset} |"
            f"{self.theme.primary}{bar}{self.theme.reset}| {ratio:.1%}"
        )
        sys.stdout.flush()
        if current >= total:
            sys.stdout.write("\n")

    def success(self, message: str):
        """Shortcut for success status output."""
        self.status("success", message, self.theme.success)

    def warning(self, message: str):
        """Shortcut for warning status output."""
        self.status("warning", message, self.theme.warning)

    def error(self, message: str):
        """Shortcut for error status output."""
        self.status("error", message, self.theme.error)


# Global singleton instance
ui = TerminalUI()
