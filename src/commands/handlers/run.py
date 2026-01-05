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
    valid, error_msg = FileValidator.validate_corplang_file(file_path)
    if not valid:
        return CLIResult(success=False, message=error_msg, exit_code=1)

    file_path = str(PathResolver.resolve_relative_path(file_path, project_root))

    EnvManager.set_module_path(project_root)

    with Timer(f"Executing {file_path}") as timer:
        try:
            ast = parse_file(file_path)
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

    project_root = CorplangConfig.get_project_root(args.file)

    strict = args.strict or EnvManager.get_corplang_strict()

    return run_file(
        args.file,
        project_root=project_root,
        verbose=args.verbose,
        strict=strict,
    )
