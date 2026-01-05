import sys
from pathlib import Path

from src.commands.config import CorplangConfig
from src.commands.utils.utils import Output, CLIResult, Colors


def get_python_version() -> str:
    """Get Python version."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_installation_path() -> str:
    """Get Corplang installation path."""
    core_path = Path(__file__).parent.parent.parent / "corplang"
    return str(core_path.resolve())


def handle_version(args) -> CLIResult:
    """CLI handler for version command."""
    version = CorplangConfig.VERSION

    Output.print(f"{Colors.BOLD}Corplang{Colors.RESET} {Colors.GREEN}v{version}{Colors.RESET}")

    if args.verbose:
        Output.print()
        Output.print(f"Installation: {get_installation_path()}")
        Output.print(f"Home:         {CorplangConfig.get_corplang_home()}")
        Output.print(f"Python:       {get_python_version()}")
        Output.print(f"Platform:     {sys.platform}")

    return CLIResult(success=True, message="")
