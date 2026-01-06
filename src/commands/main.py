#!/usr/bin/env python3
"""
Corplang CLI - Main compiler and runtime for the Corplang language.
"""

import sys
import argparse

from src.commands.config import CorplangConfig
from src.commands.utils.utils import Output, Colors, CLIResult
from src.commands.handlers import compile, run, init, version, versions, env, build, db, docs, repl, publish, uninstall, core


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="mf",
        description="Corplang - A modern language for AI-driven programming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mf run main.mp              # Execute a Corplang program
  mf compile main.mp          # Compile a program
  mf compile --dir ./src      # Compile all files in a directory
  mf init myproject           # Create a new project
  mf version --verbose        # Show version details

For more information, visit https://github.com/MF07-Language-Programing/mf07-language
""",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {CorplangConfig.VERSION}",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    create_run_parser(subparsers)
    create_compile_parser(subparsers)
    create_init_parser(subparsers)
    create_version_parser(subparsers)
    create_versions_parser(subparsers)
    create_repl_parser(subparsers)
    create_env_parser(subparsers)
    create_build_parser(subparsers)
    create_db_parser(subparsers)
    create_docs_parser(subparsers)
    create_publish_parser(subparsers)
    create_uninstall_parser(subparsers)
    create_core_parser(subparsers)

    return parser


def create_run_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'run' command."""
    parser = subparsers.add_parser(
        "run",
        help="Execute a Corplang program",
        description="Execute a .mp or .mf file",
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to .mp or .mf file to execute",
    )

    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Enable strict type checking",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.set_defaults(handler=run.handle_run)
    return parser


def create_compile_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'compile' command."""
    parser = subparsers.add_parser(
        "compile",
        help="Compile Corplang programs",
        description="Compile .mp or .mf files to AST",
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to .mp or .mf file to compile",
    )

    parser.add_argument(
        "--dir", "-d",
        dest="directory",
        help="Compile all files in directory (recursive by default)",
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file path for compiled AST (pickle format)",
    )

    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't recursively compile subdirectories",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )

    parser.set_defaults(handler=compile.handle_compile)
    return parser


def create_init_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'init' command."""
    parser = subparsers.add_parser(
        "init",
        help="Create a new Corplang project",
        description="Initialize a new Corplang project structure",
    )

    parser.add_argument(
        "name",
        nargs="?",
        help="Project name",
    )

    parser.add_argument(
        "--dir",
        help="Target directory (default: ./<name>)",
    )

    parser.set_defaults(handler=init.handle_init)
    return parser


def create_version_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'version' command."""
    parser = subparsers.add_parser(
        "version",
        help="Show version information",
        description="Display Corplang version and environment details",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed environment information",
    )

    parser.set_defaults(handler=version.handle_version)
    return parser


def create_versions_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'versions' command."""
    parser = subparsers.add_parser(
        "versions",
        help="Manage installed versions",
        description="List, set, install, repair, or uninstall Corplang versions",
    )

    sub = parser.add_subparsers(dest="versions_cmd")

    p_list = sub.add_parser("list", help="List installed versions")
    p_list.add_argument("--detailed", action="store_true", help="Show detailed info")
    p_list.add_argument("--online", action="store_true", help="Show available online versions")
    p_list.add_argument("--all-platforms", action="store_true", help="Show all platforms (disable auto-filter)")

    p_set = sub.add_parser("set", help="Set active version")
    p_set.add_argument("version", help="Version to activate")

    p_install = sub.add_parser("install", help="Install new version")
    p_install.add_argument("version", nargs="?", help="Version to install")
    p_install.add_argument("--from-url", help="Download from URL")
    p_install.add_argument("--force", action="store_true", help="Force installation")
    p_install.add_argument("--non-interactive", action="store_true", help="Skip interactive mode")

    p_repair = sub.add_parser("repair", help="Repair version")
    p_repair.add_argument("version", nargs="?", help="Version to repair")

    p_logs = sub.add_parser("logs", help="Show version logs")
    p_logs.add_argument("version", nargs="?", help="Filter logs by version")
    p_logs.add_argument("--lines", type=int, default=20, help="Number of log lines to show")

    p_upgrade = sub.add_parser("upgrade", help="Upgrade CLI binary")
    p_upgrade.add_argument("version", nargs="?", help="Version to upgrade from")

    p_uninstall = sub.add_parser(
        "purge",
        help="Uninstall a version",
    )
    p_uninstall.add_argument("version", nargs="?", help="Version to uninstall")
    p_uninstall.add_argument("--yes", "-y", action="store_true", help="Assume yes for prompts")

    p_uninstall_all = sub.add_parser(
        "purge-all",
        help="Uninstall all versions",
    )
    p_uninstall_all.add_argument("--yes", "-y", action="store_true", help="Assume yes for prompts")

    parser.set_defaults(handler=versions.handle_versions)
    return parser


def create_repl_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'repl' command."""
    parser = subparsers.add_parser(
        "repl",
        aliases=["shell", "interactive"],
        help="Interactive shell (REPL)",
        description="Start Corplang interactive shell for code evaluation",
    )

    parser.set_defaults(handler=repl.handle_repl)
    return parser


def create_env_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'env' command."""
    parser = subparsers.add_parser(
        "env",
        help="Environment management",
        description="Validate and configure environment",
    )

    sub = parser.add_subparsers(dest="env_cmd")

    p_validate = sub.add_parser("validate", help="Validate environment")
    p_config = sub.add_parser("config", help="Configuration management")
    p_config.add_argument("action", choices=["validate", "sync", "show"])

    parser.set_defaults(handler=env.handle_env)
    return parser


def create_build_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'build' command."""
    parser = subparsers.add_parser(
        "build",
        help="Build packages and executables",
        description="Build wheel, executable, or transpile to C",
    )

    parser.add_argument(
        "target",
        choices=["wheel", "exe"],
        nargs="?",
        default="wheel",
        help="Build target",
    )

    parser.set_defaults(handler=build.handle_build)
    return parser


def create_db_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'db' command."""
    parser = subparsers.add_parser(
        "db",
        help="Database operations",
        description="Manage migrations and database connections",
    )

    sub = parser.add_subparsers(dest="db_cmd")

    p_init = sub.add_parser("init", help="Initialize migrations")
    p_init.add_argument("path", nargs="?", default="migrations", help="Migrations path")

    p_connect = sub.add_parser("connect", help="Test connection")
    p_connect.add_argument("driver", help="Database driver")
    p_connect.add_argument("dsn", help="Connection string")

    sub.add_parser("makemigrations", help="Generate migrations")
    sub.add_parser("migrate", help="Apply migrations")

    parser.set_defaults(handler=db.handle_db)
    return parser


def create_docs_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'docs' command."""
    parser = subparsers.add_parser(
        "docs",
        help="Generate documentation",
        description="Generate Markdown documentation from project",
    )

    parser.add_argument("path", nargs="?", default=".", help="Project path")
    parser.add_argument("--output", default="docs", help="Output directory")
    parser.add_argument(
        "--format",
        choices=["markdown", "html", "all"],
        default="markdown",
        help="Documentation format",
    )

    parser.set_defaults(handler=docs.handle_docs)
    return parser


def create_publish_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'publish' command."""
    parser = subparsers.add_parser(
        "publish",
        help="Publish new version",
        description="Automate version bump, branch creation, and release",
    )

    bump_group = parser.add_mutually_exclusive_group()
    bump_group.add_argument(
        "--major",
        action="store_true",
        help="Bump major version (X.0.0)",
    )
    bump_group.add_argument(
        "--minor",
        action="store_true",
        help="Bump minor version (0.X.0)",
    )
    bump_group.add_argument(
        "--patch",
        action="store_true",
        help="Bump patch version (0.0.X)",
    )

    parser.add_argument(
        "--message", "-m",
        help="Release message",
    )

    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )

    parser.add_argument(
        "--skip-push",
        action="store_true",
        help="Don't push to remote (local only)",
    )

    parser.set_defaults(handler=publish.handle_publish)
    return parser


def create_uninstall_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'uninstall' command."""
    parser = subparsers.add_parser(
        "uninstall",
        help="Uninstall Corplang from your system",
        description="Remove Corplang CLI, versions, and configuration from your system",
    )

    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt",
    )

    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force removal even if directory structure looks unexpected",
    )

    parser.set_defaults(handler=uninstall.handle_uninstall)
    return parser


def create_core_parser(subparsers) -> argparse.ArgumentParser:
    """Create parser for 'core' command."""
    parser = subparsers.add_parser(
        "core",
        aliases=["stdlib", "modules"],
        help="Inspect core modules (stdlib)",
        description="Show information about core modules and stdlib",
    )

    sub = parser.add_subparsers(dest="core_cmd")

    # List command
    p_list = sub.add_parser("list", help="List all core modules")
    p_list.add_argument("--verbose", "-v", action="store_true", help="Show all modules")

    # Info command
    p_info = sub.add_parser("info", help="Show stdlib information")
    p_info.add_argument("--verbose", "-v", action="store_true", help="Show detailed info")

    # Search command
    p_search = sub.add_parser("search", help="Search for modules")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--verbose", "-v", action="store_true", help="Show detailed results")

    # Manifest command
    p_manifest = sub.add_parser("manifest", help="Show manifest contents")
    p_manifest.add_argument("--json", action="store_true", help="Output as JSON")
    p_manifest.add_argument("--verbose", "-v", action="store_true", help="Show all entries")

    parser.set_defaults(handler=core.handle_core)
    return parser


def main():
    """Main entry point for the CLI."""
    Colors.disable_if_not_tty()

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    handler = getattr(args, "handler", None)
    if not handler:
        parser.print_help()
        sys.exit(1)

    try:
        result: CLIResult = handler(args)

        if result.message:
            if result.success:
                Output.success(result.message)
            else:
                Output.error(result.message)

        sys.exit(result.exit_code)

    except KeyboardInterrupt:
        Output.warning("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        Output.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
