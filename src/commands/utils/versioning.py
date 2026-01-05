"""Semantic versioning utilities for automated release management."""

import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional


class BumpType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


class Version:
    """Semantic version representation."""

    def __init__(self, major: int, minor: int, patch: int, prerelease: Optional[str] = None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease

    @classmethod
    def parse(cls, version_str: str) -> "Version":
        """Parse version string (e.g., '1.2.3-beta.1')."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$", version_str.strip())
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        
        major, minor, patch, prerelease = match.groups()
        return cls(int(major), int(minor), int(patch), prerelease)

    def bump(self, bump_type: BumpType) -> "Version":
        """Return new version after bump."""
        if bump_type == BumpType.MAJOR:
            return Version(self.major + 1, 0, 0)
        elif bump_type == BumpType.MINOR:
            return Version(self.major, self.minor + 1, 0)
        else:  # PATCH
            return Version(self.major, self.minor, self.patch + 1)

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.prerelease}" if self.prerelease else base

    def __repr__(self) -> str:
        return f"Version({self})"


def get_current_version(pyproject_path: Path) -> Version:
    """Extract current version from pyproject.toml."""
    content = pyproject_path.read_text()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    return Version.parse(match.group(1))


def update_version_in_file(file_path: Path, new_version: Version) -> None:
    """Update version string in file."""
    content = file_path.read_text()
    updated = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        content
    )
    file_path.write_text(updated)


def get_git_tags() -> list[str]:
    """Get all git tags sorted by version."""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "v*"],
            capture_output=True,
            text=True,
            check=True
        )
        return sorted(result.stdout.strip().split("\n"), reverse=True)
    except subprocess.CalledProcessError:
        return []


def detect_bump_type_from_commits() -> BumpType:
    """Analyze commit messages since last tag to suggest bump type."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--no-decorate"],
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.lower()
        
        if "breaking" in commits or "!:" in commits:
            return BumpType.MAJOR
        elif "feat" in commits or "feature" in commits:
            return BumpType.MINOR
        else:
            return BumpType.PATCH
    except subprocess.CalledProcessError:
        return BumpType.PATCH


def create_git_tag(version: Version, message: str = "") -> bool:
    """Create annotated git tag for version."""
    tag = f"v{version}"
    msg = message or f"Release {tag}"
    try:
        subprocess.run(
            ["git", "tag", "-a", tag, "-m", msg],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def push_tag(tag: str) -> bool:
    """Push tag to remote."""
    try:
        subprocess.run(
            ["git", "push", "origin", tag],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
