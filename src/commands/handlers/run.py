from pathlib import Path
from typing import Optional

from src.corplang.executor import execute, parse_file
from src.corplang.tools.diagnostics import format_exception

from src.commands.config import CorplangConfig
from src.commands.utils.utils import (
    Output,
    FileValidator,
    Timer,
    CLIResult,
    PathResolver,
    EnvManager,
)


def run_file(
        file_path: str,
        project_root: Optional[Path] = None,
        verbose: bool = False,
        strict: bool = False,
) -> CLIResult:
    """Execute a .mp file."""
    # file_path is already resolved, just validate
    valid, error_msg = FileValidator.validate_corplang_file(file_path)
    if not valid:
        return CLIResult(success=False, message=error_msg, exit_code=1)

    EnvManager.set_module_path(project_root)

    with Timer(f"Executing {file_path}") as timer:
        try:
            ast = parse_file(file_path, verbose)
            Output.debug(f"Parsed {len(ast.statements)} statements", verbose)

            result = execute(ast)

            timer.report()
            return CLIResult(success=True, message="Execution successful")

        except Exception as e:
            error_output = format_exception(e)
            return CLIResult(
                success=False,
                message=f"Execution failed:\n{error_output}",
                exit_code=1,
            )


def handle_run(args) -> CLIResult:
    """CLI handler for run command."""
    if not args.file:
        return CLIResult(
            success=False,
            message="No file specified. Use: mf run <file.mp>",
            exit_code=1,
        )

    # Resolve path first to get actual file location
    resolved_path = PathResolver.resolve_relative_path(args.file)

    # Then get project root from resolved path
    project_root = CorplangConfig.get_project_root(str(resolved_path))

    strict = args.strict or EnvManager.get_corplang_strict()

    return run_file(
        str(resolved_path),
        project_root=project_root,
        verbose=args.verbose,
        strict=strict,
    )
