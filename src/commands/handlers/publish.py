"""Publish command handler - automated version management and release."""

import subprocess
from pathlib import Path

from src.commands.utils.utils import Output, CLIResult
from src.commands.utils.versioning import (
    BumpType,
    Version,
    get_current_version,
    update_version_in_file,
    detect_bump_type_from_commits,
)


def handle_publish(args) -> CLIResult:
    """
    Publish new version with automated commits.
    
    Workflow:
    1. Detect or use specified bump type (major/minor/patch)
    2. Calculate new version
    3. Update pyproject.toml version (language/package version)
    4. Commit pyproject.toml changes
    5. Update CLI version (src/commands/config.py)
    6. Commit CLI version separately
    7. Push to main branch
    """
    try:
        root = Path.cwd()
        pyproject = root / "pyproject.toml"
        cli_config = root / "src/commands/config.py"

        if not pyproject.exists():
            return CLIResult(
                success=False,
                message="pyproject.toml not found in current directory"
            )

        current_version = get_current_version(pyproject)
        Output.info(f"Current version: {current_version}")

        bump_type = _determine_bump_type(args)
        new_version = current_version.bump(bump_type)

        Output.info(f"New version: {new_version} ({bump_type.value} bump)")

        if not args.yes and not _confirm(f"Publish version {new_version}?"):
            return CLIResult(success=False, message="Publish cancelled by user")

        if not _ensure_clean_working_tree():
            return CLIResult(
                success=False,
                message="Working tree has uncommitted changes. Commit or stash them first."
            )

        Output.step("Updating pyproject.toml version...")
        update_version_in_file(pyproject, new_version)

        Output.info("Committing pyproject.toml...")
        if not _commit_file(pyproject, f"chore: bump language version to {new_version}"):
            return CLIResult(
                success=False,
                message="Failed to commit pyproject.toml"
            )
        Output.success(f"✓ Committed pyproject.toml ({new_version})")

        # Update CLI version separately
        Output.step("Updating CLI version...")
        if not _update_cli_version(cli_config, new_version):
            return CLIResult(
                success=False,
                message="Failed to update CLI version in config.py"
            )

        Output.info("Committing CLI version...")
        if not _commit_file(cli_config, f"chore: bump CLI version to {new_version}"):
            return CLIResult(
                success=False,
                message="Failed to commit config.py"
            )
        Output.success(f"✓ Committed CLI version ({new_version})")

        # Push to main
        if not args.skip_push:
            Output.info("Pushing to main...")
            if not _push_to_main():
                Output.warning("Push failed. Changes committed locally.")
                Output.info("Run manually: git push origin main")
                return CLIResult(
                    success=True,
                    message=f"Version {new_version} committed locally. Manual push required."
                )

        Output.success(f"✓ Version {new_version} published successfully!")
        Output.info(f"  - pyproject.toml: {new_version}")
        Output.info(f"  - CLI version: {new_version}")
        Output.info(f"  - Branch: main")

        # Show version check
        Output.step("Verifying installation...")
        _check_cli_version()

        return CLIResult(
            success=True,
            message=f"Published version {new_version}"
        )

    except Exception as e:
        return CLIResult(
            success=False,
            message=f"Publish failed: {e}"
        )


def _determine_bump_type(args) -> BumpType:
    """Determine bump type from args or commits."""
    if args.major:
        return BumpType.MAJOR
    elif args.minor:
        return BumpType.MINOR
    elif args.patch:
        return BumpType.PATCH
    else:
        detected = detect_bump_type_from_commits()
        Output.info(f"Auto-detected bump type: {detected.value}")
        return detected


def _ensure_clean_working_tree() -> bool:
    """Check if working tree is clean."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        return len(result.stdout.strip()) == 0
    except subprocess.CalledProcessError:
        return False


def _commit_file(file_path: Path, message: str) -> bool:
    """Commit a specific file with message (signed)."""
    try:
        subprocess.run(
            ["git", "add", str(file_path)],
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-S", "-m", message],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _update_cli_version(config_file: Path, version: Version) -> bool:
    """Update VERSION in src/commands/config.py"""
    try:
        content = config_file.read_text()
        # Replace VERSION = "x.y.z" with new version
        import re
        new_content = re.sub(
            r'VERSION = "[^"]+"',
            f'VERSION = "{version}"',
            content
        )
        config_file.write_text(new_content)
        return True
    except Exception:
        return False


def _push_to_main() -> bool:
    """Push to main branch."""
    try:
        subprocess.run(
            ["git", "push", "origin", "main"],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _check_cli_version() -> None:
    """Check and display CLI version."""
    try:
        result = subprocess.run(
            ["./mf", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            Output.info(f"CLI version: {result.stdout.strip()}")
    except Exception:
        pass


def _confirm(prompt: str) -> bool:
    """Simple confirmation prompt."""
    response = input(f"{prompt} [y/N]: ").strip().lower()
    return response in ["y", "yes"]
