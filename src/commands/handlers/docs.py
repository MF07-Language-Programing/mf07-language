from pathlib import Path

from src.commands.utils.utils import Output, CLIResult


def generate_docs(
    project_path: str,
    output_dir: str = "docs",
    doc_format: str = "markdown",
) -> CLIResult:
    """Generate documentation from project."""
    proj_path = Path(project_path)

    if not proj_path.exists():
        return CLIResult(
            success=False,
            message=f"Project path not found: {project_path}",
            exit_code=1,
        )

    mp_files = list(proj_path.glob("**/*.mp"))

    if not mp_files:
        return CLIResult(
            success=False,
            message=f"No .mp files found in {project_path}",
            exit_code=1,
        )

    output_path = proj_path / output_dir
    output_path.mkdir(exist_ok=True, parents=True)

    Output.section(f"Generating Documentation")
    Output.print(f"Project: {proj_path}")
    Output.print(f"Output:  {output_path}")
    Output.print(f"Files:   {len(mp_files)} .mp file(s) found")

    try:
        generated = 0

        for mp_file in mp_files:
            relative = mp_file.relative_to(proj_path)
            doc_file = output_path / f"{relative.stem}.md"
            doc_file.parent.mkdir(exist_ok=True, parents=True)

            docstring = _extract_docstring(str(mp_file))
            content = f"# {relative.stem}\n\n"
            if docstring:
                content += f"{docstring}\n\n"
            content += f"**Source:** `{relative}`\n"

            doc_file.write_text(content)
            generated += 1

        Output.success(f"Generated {generated} documentation file(s)")
        return CLIResult(success=True, message="Documentation generated")

    except Exception as e:
        return CLIResult(success=False, message=f"Generation failed: {e}", exit_code=1)


def _extract_docstring(file_path: str) -> str:
    """Extract docstring from .mp file."""
    try:
        with open(file_path) as f:
            lines = f.readlines()[:10]

        for line in lines:
            if line.strip().startswith("#"):
                return line.strip().lstrip("# ")

        return ""
    except Exception:
        return ""


def handle_docs(args) -> CLIResult:
    """CLI handler for docs command."""
    project_path = getattr(args, "path", ".")
    output_dir = getattr(args, "output", "docs")
    doc_format = getattr(args, "format", "markdown")

    return generate_docs(project_path, output_dir, doc_format)
