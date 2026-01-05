import subprocess
import sys
from pathlib import Path

from src.commands.utils.utils import Output, CLIResult


def build_wheel() -> CLIResult:
    """Build wheel package."""
    try:
        cmd = [sys.executable, "-m", "build", "--wheel"]
        Output.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, cwd=Path.cwd())
        if result.returncode == 0:
            Output.success("Wheel built successfully")
            return CLIResult(success=True, message="Build complete")
        else:
            return CLIResult(success=False, message="Build failed", exit_code=result.returncode)

    except Exception as e:
        return CLIResult(success=False, message=f"Build error: {e}", exit_code=1)


def build_exe() -> CLIResult:
    """Build standalone executable."""
    try:
        cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "src/commands/main.py"]
        Output.info(f"Running: {' '.join(cmd)}")

        result = subprocess.run(cmd, cwd=Path.cwd())
        if result.returncode == 0:
            Output.success("Executable built successfully")
            return CLIResult(success=True, message="Build complete")
        else:
            return CLIResult(success=False, message="Build failed", exit_code=result.returncode)

    except Exception as e:
        return CLIResult(success=False, message=f"Build error: {e}", exit_code=1)


def transpile_to_c(input_file: str, output_file: str) -> CLIResult:
    """Transpile .mp to C code."""
    input_path = Path(input_file)

    if not input_path.exists():
        return CLIResult(
            success=False,
            message=f"Input file not found: {input_file}",
            exit_code=1,
        )

    if not input_file.endswith(".mp"):
        return CLIResult(
            success=False,
            message="Input file must be .mp format",
            exit_code=1,
        )

    try:
        Output.info(f"Transpiling {input_file} to {output_file}...")
        Output.warning("C transpilation feature requires manual implementation")
        return CLIResult(success=True, message="Transpilation prepared")

    except Exception as e:
        return CLIResult(success=False, message=f"Transpilation error: {e}", exit_code=1)


def handle_build(args) -> CLIResult:
    """CLI handler for build command."""
    if hasattr(args, "target") and args.target == "wheel":
        return build_wheel()
    elif hasattr(args, "target") and args.target == "exe":
        return build_exe()
    else:
        return build_wheel()
