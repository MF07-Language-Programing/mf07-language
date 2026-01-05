from pathlib import Path

from src.commands.utils.utils import Output, CLIResult, safe_write_file


DEFAULT_LANGUAGE_CONFIG = """# Corplang Project Configuration

# Project name
name: ""

# Project description
description: ""

# Language version
language_version: "0.1.0"

# Module search paths
module_paths:
  - ./lib
  - ./src
  - ./modules

# Compilation settings
compile:
  # Enable strict type checking
  strict: false
  # Target Python version
  target: "3.9"
  # Enable optimization
  optimize: false
  # Enable inline native calls
  native_inline: true

# Runtime settings
runtime:
  # Maximum recursion depth
  max_recursion: 10000
  # Enable async/await
  async_enabled: true
  # Memory limit in MB (0 = unlimited)
  memory_limit: 0

# Development settings
dev:
  # Enable debug output
  debug: false
  # Enable UI feedback
  ui_enabled: true
"""

DEFAULT_MAIN_MP = '''# main.mp - Corplang Program Entry Point

intent main() {
    print("🎉 Welcome to Corplang!")
    print("Edit this file to start coding...")
}

await main()
'''

DEFAULT_README = """# {project_name}

A Corplang project.

## Structure

```
├── main.mp          # Entry point
├── lib/             # Local libraries
├── src/             # Source modules
└── language_config.yaml  # Project configuration
```

## Running

```bash
mf run main.mp
```

## Compiling

```bash
mf compile main.mp
```

## Building

```bash
mf build
```
"""

GITIGNORE = """# Corplang cache
.corplang-cache/

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""


def create_project_structure(project_name: str, target_dir: str) -> CLIResult:
    """Create a new Corplang project structure."""
    target_path = Path(target_dir)

    if target_path.exists() and list(target_path.iterdir()):
        return CLIResult(
            success=False,
            message=f"Directory {target_dir} already exists and is not empty",
            exit_code=1,
        )

    try:
        target_path.mkdir(exist_ok=True, parents=True)

        config = DEFAULT_LANGUAGE_CONFIG.replace("", project_name)
        safe_write_file(str(target_path / "language_config.yaml"), config)

        safe_write_file(str(target_path / "main.mp"), DEFAULT_MAIN_MP)

        safe_write_file(
            str(target_path / "README.md"),
            DEFAULT_README.format(project_name=project_name),
        )

        safe_write_file(str(target_path / ".gitignore"), GITIGNORE)

        (target_path / "lib").mkdir(exist_ok=True)
        (target_path / "src").mkdir(exist_ok=True)
        (target_path / "modules").mkdir(exist_ok=True)

        safe_write_file(
            str(target_path / "lib" / ".gitkeep"),
            "# Keep this directory\n",
        )
        safe_write_file(
            str(target_path / "src" / ".gitkeep"),
            "# Keep this directory\n",
        )
        safe_write_file(
            str(target_path / "modules" / ".gitkeep"),
            "# Keep this directory\n",
        )

        return CLIResult(
            success=True,
            message=f"Project '{project_name}' created in {target_dir}",
        )

    except Exception as e:
        return CLIResult(
            success=False,
            message=f"Failed to create project: {e}",
            exit_code=1,
        )


def handle_init(args) -> CLIResult:
    """CLI handler for init command."""
    project_name = args.name or Path(args.dir or ".").name or "corplang-project"
    target_dir = args.dir or f"./{project_name}"

    Output.section(f"Initializing Corplang project: {project_name}")

    result = create_project_structure(project_name, target_dir)

    if result.success:
        Output.success(result.message)
        Output.print()
        Output.info("Next steps:")
        Output.print(f"  cd {target_dir}")
        Output.print("  mf run main.mp")
    else:
        Output.error(result.message)

    return result
