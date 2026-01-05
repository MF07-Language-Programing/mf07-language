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
    Create release branch with version bump.
    
    Workflow:
    1. Detect or use specified bump type (major/minor/patch)
    2. Calculate new version
    3. Create release branch
    4. Update version in pyproject.toml
    5. Commit changes
    6. Push branch to remote (GitHub Actions will handle tag/release)
    """
    try:
        root = Path.cwd()
        pyproject = root / "pyproject.toml"

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

        branch_name = f"release/v{new_version}"

        if not _ensure_clean_working_tree():
            return CLIResult(
                success=False,
                message="Working tree has uncommitted changes. Commit or stash them first."
            )

        Output.info("Creating release branch...")
        if not _create_branch(branch_name):
            return CLIResult(
                success=False,
                message=f"Failed to create branch {branch_name}"
            )

        Output.info("Updating version in pyproject.toml...")
        update_version_in_file(pyproject, new_version)

        Output.info("Committing version bump...")
        if not _commit_version_bump(new_version):
            _cleanup_branch(branch_name)
            return CLIResult(
                success=False,
                message="Failed to commit version changes"
            )

        if not args.skip_push:
            Output.info("Pushing branch to remote...")
            if not _push_branch(branch_name):
                Output.warning("Push failed. Branch created locally.")
                Output.info(f"Run manually: git push -u origin {branch_name}")
                return CLIResult(
                    success=True,
                    message=f"Version {new_version} prepared locally. Manual push required."
                )

        Output.success(f"✓ Version {new_version} published successfully!")
        Output.info(f"  Branch: {branch_name}")
        Output.info(f"  Next: Create PR to main → GitHub Actions will handle tag & release")

        return CLIResult(
            success=True,
            message=f"Published version {new_version} on branch {branch_name}"
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


def _create_branch(branch_name: str) -> bool:
    """Create and checkout new branch."""
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _commit_version_bump(version: Version) -> bool:
    """Commit version changes."""
    try:
        subprocess.run(
            ["git", "add", "pyproject.toml"],
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"chore: bump version to {version}"],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _push_branch(branch: str) -> bool:
    """Push branch to remote."""
    try:
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _cleanup_branch(branch: str) -> None:
    """Cleanup failed branch."""
    try:
        subprocess.run(["git", "checkout", "-"], check=False, capture_output=True)
        subprocess.run(["git", "branch", "-D", branch], check=False, capture_output=True)
    except Exception:
        pass


def _confirm(prompt: str) -> bool:
    """Simple confirmation prompt."""
    response = input(f"{prompt} [y/N]: ").strip().lower()
    return response in ["y", "yes"]
