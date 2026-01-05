from pathlib import Path
from typing import Optional

from src.corplang.compiler import Lexer
from src.corplang.compiler.parser import Parser
from src.corplang.tools.diagnostics import format_exception

from src.commands.config import CorplangConfig
from src.commands.utils.utils import (
    Output,
    FileValidator,
    Timer,
    CLIResult,
    PathResolver,
    safe_load_file,
)


def compile_file(
    file_path: str,
    output_path: Optional[str] = None,
    project_root: Optional[Path] = None,
    verbose: bool = False,
) -> CLIResult:
    """Compile a single .mp file."""
    valid, error_msg = FileValidator.validate_corplang_file(file_path)
    if not valid:
        return CLIResult(success=False, message=error_msg, exit_code=1)

    file_path = str(PathResolver.resolve_relative_path(file_path, project_root))

    with Timer(f"Compiling {file_path}") as timer:
        source = safe_load_file(file_path)
        if source is None:
            return CLIResult(success=False, message="Failed to load file", exit_code=1)

        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens, source_file=file_path)
            ast = parser.parse()

            Output.debug(f"Parsed {len(tokens)} tokens", verbose)
            Output.debug(f"Generated AST with {len(ast.statements)} statements", verbose)

            if output_path:
                import pickle
                try:
                    output_dir = Path(output_path).parent
                    output_dir.mkdir(exist_ok=True, parents=True)
                    with open(output_path, "wb") as f:
                        pickle.dump(ast, f)
                    Output.success(f"Compiled to {output_path}")
                except Exception as e:
                    return CLIResult(
                        success=False,
                        message=f"Failed to write output: {e}",
                        exit_code=1,
                    )

            timer.report()
            return CLIResult(success=True, message="Compilation successful")

        except Exception as e:
            error_output = format_exception(e)
            return CLIResult(
                success=False,
                message=f"Compilation failed:\n{error_output}",
                exit_code=1,
            )


def compile_directory(
    directory: str,
    recursive: bool = True,
    project_root: Optional[Path] = None,
    verbose: bool = False,
) -> CLIResult:
    """Compile all .mp files in a directory."""
    dir_path = Path(directory)
    if not dir_path.exists():
        return CLIResult(
            success=False,
            message=f"Directory not found: {directory}",
            exit_code=1,
        )

    files = FileValidator.find_corplang_files(str(dir_path), recursive=recursive)
    if not files:
        return CLIResult(
            success=False,
            message=f"No .mp or .mf files found in {directory}",
            exit_code=1,
        )

    Output.section(f"Compiling {len(files)} file(s)")

    failed = []
    with Timer(f"Directory compilation") as timer:
        for file_path in files:
            relative_path = str(PathResolver.get_relative_to_cwd(file_path))
            result = compile_file(str(file_path), project_root=project_root, verbose=verbose)
            if result.success:
                Output.success(f"Compiled {relative_path}")
            else:
                Output.error(f"Failed: {relative_path}")
                failed.append((relative_path, result.message))

        timer.report()

    if failed:
        Output.section("Compilation Errors")
        for file_path, error_msg in failed:
            Output.print(f"\n{file_path}:")
            Output.print(error_msg)
        return CLIResult(
            success=False,
            message=f"{len(failed)} file(s) failed to compile",
            exit_code=1,
        )

    return CLIResult(success=True, message=f"All {len(files)} file(s) compiled successfully")


def handle_compile(args) -> CLIResult:
    """CLI handler for compile command."""
    project_root = CorplangConfig.get_project_root(args.file or ".")

    if args.directory:
        return compile_directory(
            args.directory,
            recursive=not args.no_recursive,
            project_root=project_root,
            verbose=args.verbose,
        )
    else:
        return compile_file(
            args.file,
            output_path=args.output,
            project_root=project_root,
            verbose=args.verbose,
        )
