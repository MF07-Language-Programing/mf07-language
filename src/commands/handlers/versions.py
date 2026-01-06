import platform
import threading
from pathlib import Path
from typing import List

from src.commands.config import VersionManager
from src.commands.utils.utils import Output, CLIResult, Colors, Timer, Spinner, SelectMenu


def list_online_releases(limit: int = 10, filter_platform: bool = True) -> List[dict]:
    """Fetch and display online releases from GitHub."""
    vm = VersionManager()
    Output.info("Fetching releases from GitHub...")

    releases = vm.fetch_remote_releases()
    if not releases:
        Output.warning("Could not fetch releases from GitHub")
        return []

    if filter_platform:
        current_platform = platform.system().lower()
        platform_map = {
            'linux': '-linux',
            'darwin': '-macos',
            'windows': '-windows',
        }
        platform_suffix = platform_map.get(current_platform, '')

        filtered = []
        for release in releases:
            tag = release.get('tag_name', '').lower()
            # Include it if: has a current platform suffix OR has no platform suffix
            has_platform_suffix = any(tag.endswith(suffix) for suffix in platform_map.values())

            if not has_platform_suffix:
                # Generic release, include it
                filtered.append(release)
            elif platform_suffix and tag.endswith(platform_suffix):
                # Matches current platform
                filtered.append(release)

        releases = filtered

    return releases[:limit]


def list_versions(detailed: bool = False, show_online: bool = False, all_platforms: bool = False) -> CLIResult:
    """List all installed versions and optionally online versions."""
    vm = VersionManager()
    versions = vm.list_versions(detailed=detailed)

    if not versions and not show_online:
        return CLIResult(
            success=False,
            message="No versions installed",
            exit_code=1,
        )

    Output.section("Installed Versions")
    active = vm.get_active_version()

    if versions:
        for version, info in sorted(versions.items()):
            status = "✓" if info["valid"] else "✗"
            marker = " (active)" if version == active else ""
            installed_at = info.get("installed_at", "")
            Output.print(f"  {status} {Colors.BOLD}{version}{Colors.RESET}{marker}")

            if detailed:
                Output.print(f"     Path:     {info['path']}")
                Output.print(f"     Type:     {info['type']}")
                if installed_at:
                    Output.print(f"     Installed: {installed_at}")
                Output.print()

    if show_online:
        current_platform = platform.system().lower()
        platform_names = {'linux': 'Linux', 'darwin': 'macOS', 'windows': 'Windows'}
        platform_name = platform_names.get(current_platform, current_platform)

        if all_platforms:
            Output.section("Available Online (All Platforms)")
        else:
            Output.section(f"Available Online ({platform_name})")

        releases = list_online_releases(filter_platform=not all_platforms)
        if releases:
            for i, release in enumerate(releases[:5], 1):
                tag = release.get("tag_name", "unknown")
                prerelease = " (pre-release)" if release.get("prerelease") else ""
                Output.print(f"  {i}. {Colors.BOLD}{tag}{Colors.RESET}{prerelease}")
                if detailed:
                    published = release.get("published_at", "")
                    if published:
                        Output.print(f"     Released: {published}")
                    Output.print()
        else:
            Output.warning("No releases available online")

    return CLIResult(success=True, message=f"Listed {len(versions)} version(s)")


def set_version(version: str) -> CLIResult:
    """Set the active version."""
    vm = VersionManager()
    versions = vm.list_versions()

    if version not in versions:
        return CLIResult(
            success=False,
            message=f"Version '{version}' not found",
            exit_code=1,
        )

    if not versions[version]["valid"]:
        return CLIResult(
            success=False,
            message=f"Version '{version}' is invalid",
            exit_code=1,
        )

    if vm.set_active_version(version):
        Output.success(f"Active version set to {version}")
        Output.info("Environment variable CORPLANG_ACTIVE_VERSION has been set")
        Output.warning("Restart your shell or run: source ~/.bashrc (or ~/.zshrc)")
        return CLIResult(success=True, message=f"Version {version} is now active")
    else:
        return CLIResult(
            success=False,
            message="Failed to set version",
            exit_code=1,
        )


def install_version(
        version: str = None,
        from_url: str = None,
        force: bool = False,
        interactive: bool = True,
) -> CLIResult:
    """Install a new version from GitHub or custom URL."""
    vm = VersionManager()
    versions = vm.list_versions()

    if not version and interactive:
        platform_name = {'linux': 'Linux', 'darwin': 'macOS', 'windows': 'Windows'}.get(
            platform.system().lower(), platform.system()
        )
        Output.section(f"Install Version ({platform_name})")

        releases = list_online_releases()
        if not releases:
            return CLIResult(False, "Could not fetch available versions", 1)

        available = [r for r in releases if r["tag_name"] not in versions]
        if not available:
            Output.warning("All available versions are already installed")
            return CLIResult(False, "No new versions to install", 0)

        version = SelectMenu([r["tag_name"] for r in available], "Select version:").show()
        if not version:
            return CLIResult(False, "Installation cancelled", 1)

    if not version:
        return CLIResult(False, "Version required", 1)

    if version in versions and not force:
        return CLIResult(False, f"Version {version} already installed (use --force)", 1)

    Output.section(f"Installing {version}")

    # Get release info for CLI binary
    releases = vm.fetch_remote_releases()
    target_release = next((r for r in releases if r["tag_name"] == version), None)
    cli_asset = None
    cli_checksum = None

    if target_release:
        platform_suffix = {'linux': 'mf', 'darwin': 'mf', 'windows': 'mf.exe'}[
            platform.system().lower()
        ]
        assets = target_release.get("assets", [])
        cli_asset = next((a for a in assets if a["name"] == platform_suffix), None)
        cli_checksum = next((a for a in assets if a["name"] == f"{platform_suffix}.sha256"), None)

    spinner = Spinner("Downloading source...")
    try:
        threading.Thread(target=spinner.start, daemon=True).start()
        target_dir = vm.download_version(version, from_url)
        spinner.stop(success=bool(target_dir))

        if not target_dir:
            vm.log_action("INSTALL", version, "FAILED", "download error")
            return CLIResult(False, f"Failed to install {version}", 1)

        # Ask about CLI installation (global)
        cli_installed = False
        if cli_asset and interactive:
            size_mb = cli_asset["size"] / (1024 * 1024)
            Output.print(f"\n💡 CLI binary available: {cli_asset['name']} ({size_mb:.1f}MB)")
            choice = input(f"{Colors.GREEN}Install CLI globally (~/.corplang)? (Y/n): {Colors.RESET}").strip().lower()

            if choice in ('', 'y', 'yes'):
                cli_spinner = Spinner("Downloading CLI...")
                threading.Thread(target=cli_spinner.start, daemon=True).start()
                cli_installed = vm.download_cli_binary(
                    version,
                    cli_asset["url"],
                    cli_checksum["url"] if cli_checksum else None,
                )
                cli_spinner.stop(success=cli_installed)
                if cli_installed:
                    vm.configure_cli_environment()

        Output.print()
        _show_installation_tree(target_dir, version, cli_installed)
        Output.success(f"\n✓ Version {version} installed: {target_dir}")

        vm.log_action("INSTALL", version, "SUCCESS", target_dir)
        return CLIResult(True, f"Version {version} installed successfully")

    except Exception as e:
        if 'spinner' in locals():
            spinner.stop(success=False)
        vm.log_action("INSTALL", version, "ERROR", str(e))
        return CLIResult(False, f"Installation error: {str(e)}", 1)


def uninstall_version(version: str = None, all_versions: bool = False, assume_yes: bool = False) -> CLIResult:
    """Uninstall one version or all installed versions."""
    vm = VersionManager()
    versions = vm.list_versions()

    # Remove all
    if all_versions:
        if not assume_yes:
            choice = input(f"{Colors.YELLOW}Remove ALL installed versions? (y/N): {Colors.RESET}").strip().lower()
            if choice not in ("y", "yes"):
                return CLIResult(False, "Cancelled", 1)

        removed = vm.uninstall_all_versions()
        return CLIResult(True, f"Removed {removed} version(s)")

    # Remove single
    installed = [v for v in versions.keys() if v != "local"]
    if not installed:
        return CLIResult(False, "No installed versions to remove", 1)

    if not version:
        version = SelectMenu(installed, "Select version to uninstall:").show()
        if not version:
            return CLIResult(False, "Cancelled", 1)

    if version not in versions or version == "local":
        return CLIResult(False, f"Version '{version}' not found", 1)

    if not assume_yes:
        confirm = input(f"{Colors.YELLOW}Uninstall {version}? (y/N): {Colors.RESET}").strip().lower()
        if confirm not in ("y", "yes"):
            return CLIResult(False, "Cancelled", 1)

    if vm.uninstall_version(version):
        return CLIResult(True, f"Uninstalled {version}")

    return CLIResult(False, "Failed to uninstall", 1)


def _show_installation_tree(target_dir: str, version: str, cli_installed: bool = False):
    """Display the installation structure with CLI binaries detection."""
    root = Path(target_dir)
    if not root.exists():
        return

    Output.section(f"Installation: {version}")

    # Global CLI location
    from src.commands.config import CorplangConfig
    base_dir = CorplangConfig.get_corplang_home()
    platform_suffix = {'linux': 'mf', 'darwin': 'mf', 'windows': 'mf.exe'}[
        platform.system().lower()
    ]
    global_cli = base_dir / platform_suffix
    global_cli_status = "✓" if global_cli.exists() else "✗"
    Output.print(f"  🚀 CLI (global): {global_cli_status} {global_cli}")

    # Detect CLI binaries inside the version folder (should be none after change)
    cli_binaries = [f for f in root.glob('mf*') if f.is_file() and f.suffix != '.sha256']
    if cli_binaries:
        for binary in cli_binaries:
            size = binary.stat().st_size / (1024 * 1024)
            Output.print(f"     (local) {binary.name} ({size:.1f}MB)")
    elif cli_installed:
        Output.print("     CLI downloaded to global home")
    else:
        Output.print(f"     {Colors.DIM}CLI not installed for this version{Colors.RESET}")

    # Key directories
    paths = {
        'src/corplang/compiler': '⚙️  Compiler',
        'src/corplang/executor': '▶️  Executor',
        'src/corplang/stdlib': '📚 Stdlib',
        'examples': '📋 Examples',
    }

    for path, desc in paths.items():
        full = root / path
        if full.exists() and full.is_dir():
            count = sum(1 for _ in full.iterdir())
            Output.print(f"  {desc}: {count} items")

    # Statistics
    py_files = list(root.rglob('*.py'))
    mp_files = list(root.rglob('*.mp'))
    total_size = sum(f.stat().st_size for f in root.rglob('*') if f.is_file()) / (1024 * 1024)

    Output.print(f"\n  📊 {len(py_files)} Python • {len(mp_files)} Examples • {total_size:.1f}MB")


def repair_version(version: str = None) -> CLIResult:
    """Repair a corrupted version."""
    vm = VersionManager()
    versions = vm.list_versions()

    if not version and len(versions) == 1:
        version = list(versions.keys())[0]
    elif not version:
        menu = SelectMenu(list(versions.keys()), "Select version to repair:")
        version = menu.show()
        if not version:
            return CLIResult(success=False, message="Repair cancelled", exit_code=1)

    if version not in versions:
        return CLIResult(
            success=False,
            message=f"Version '{version}' not found",
            exit_code=1,
        )

    version_path = versions[version]["path"]

    with Timer(f"Repairing version {version}") as timer:
        required_files = [
            "src/corplang/compiler/lexer.py",
            "src/corplang/compiler/parser.py",
            "src/corplang/executor/__init__.py",
        ]

        missing = [f for f in required_files if not (Path(version_path) / f).exists()]

        if not missing:
            Output.success("Version is already valid")
            vm.log_action("REPAIR", version, "VALID", "no issues found")
            return CLIResult(success=True, message=f"Version {version} is valid")

        Output.warning(f"Found {len(missing)} missing file(s):")
        for f in missing:
            Output.print(f"  - {f}")

        Output.info("Attempting to re-download missing components...")
        if vm.download_version(version):
            Output.success("Repair completed successfully")
            vm.log_action("REPAIR", version, "REPAIRED", "missing files restored")
            timer.report()
            return CLIResult(success=True, message=f"Version {version} repaired")
        else:
            Output.error("Could not repair version")
            vm.log_action("REPAIR", version, "FAILED", "re-download unsuccessful")
            return CLIResult(
                success=False,
                message=f"Failed to repair version {version}",
                exit_code=1,
            )


def show_version_logs(version: str = None, lines: int = 20) -> CLIResult:
    """Show logs for version operations."""
    vm = VersionManager()

    if version:
        Output.section(f"Logs for {version}")
    else:
        Output.section("Version Manager Logs")

    logs = vm.get_version_logs(version, limit=lines)
    if not logs:
        Output.info("No logs available")
        return CLIResult(success=True, message="No logs")

    for log in logs:
        parts = log.strip().split(" | ")
        if len(parts) < 4:
            Output.print(log.strip())
            continue

        timestamp = parts[0]
        action = parts[1].strip()
        version_name = parts[2].strip()
        status = parts[3].strip()
        details = " | ".join(parts[4:]).strip() if len(parts) > 4 else ""

        icons = {
            "SUCCESS": "✓",
            "REPAIRED": "✓",
            "VALID": "✓",
            "STARTED": "…",
            "FAILED": "✗",
            "ERROR": "✗",
        }
        colors = {
            "SUCCESS": Colors.GREEN,
            "REPAIRED": Colors.GREEN,
            "VALID": Colors.GREEN,
            "STARTED": Colors.YELLOW,
            "FAILED": Colors.RED,
            "ERROR": Colors.RED,
        }

        verbs = {
            "INSTALL": "Installed",
            "DOWNLOAD": "Downloaded",
            "CLI_DOWNLOAD": "CLI downloaded",
            "SET_ACTIVE": "Activated",
            "REPAIR": "Repair",
            "UNINSTALL": "Uninstalled",
            "UNINSTALL_ALL": "Purged",
            "UPGRADE": "Upgraded",
        }

        icon = icons.get(status, "•")
        color = colors.get(status, Colors.CYAN)
        verb = verbs.get(action, action.title())
        detail_text = f" ({details})" if details else ""

        Output.print(
            f"{timestamp}  {color}{icon} {status:<8}{Colors.RESET} {verb} {version_name}{detail_text}"
        )

    return CLIResult(success=True, message="Logs displayed")


def upgrade_cli(version: str = None) -> CLIResult:
    """Upgrade global CLI binary. Prefers release asset; falls back to local copy."""
    vm = VersionManager()
    versions = vm.list_versions()

    if not version:
        version = vm.get_active_version() or next(iter(versions.keys()), None)

    if not version or version not in versions:
        return CLIResult(False, "No valid version found", 1)

    platform_suffix = {'linux': 'mf', 'darwin': 'mf', 'windows': 'mf.exe'}[platform.system().lower()]

    # Try downloading CLI from release assets
    releases = vm.fetch_remote_releases()
    target_release = next((r for r in releases if r.get("tag_name") == version), None)
    asset = None
    checksum = None
    if target_release:
        assets = target_release.get("assets", [])
        asset = next((a for a in assets if a.get("name") == platform_suffix), None)
        checksum = next((a for a in assets if a.get("name") == f"{platform_suffix}.sha256"), None)

    if asset:
        ok = vm.download_cli_binary(
            version,
            asset.get("url", ""),
            checksum.get("url", "") if checksum else None,
        )
        if ok:
            vm.configure_cli_environment()
            target_cli = Path.home() / ".corplang" / platform_suffix
            Output.success(f"CLI upgraded to {version}")
            Output.info(f"Binary: {target_cli}")
            return CLIResult(True, f"CLI upgraded successfully")

    # Fallback: copy from local version directory if present
    version_path = Path(versions[version]["path"])
    cli_binary = version_path / platform_suffix

    if not cli_binary.exists():
        return CLIResult(False, f"CLI binary not found in release or local for {version}", 1)

    import shutil
    base_dir = Path.home() / ".corplang"
    base_dir.mkdir(exist_ok=True)
    target_cli = base_dir / platform_suffix
    shutil.copy2(cli_binary, target_cli)
    target_cli.chmod(0o755)

    vm.configure_cli_environment()
    Output.success(f"CLI upgraded to {version}")
    Output.info(f"Binary: {target_cli}")

    return CLIResult(True, f"CLI upgraded successfully")


def handle_versions(args) -> CLIResult:
    """CLI handler for versions command."""
    cmd_map = {
        "list": lambda: list_versions(
            getattr(args, "detailed", False),
            getattr(args, "online", False),
            getattr(args, "all_platforms", False)
        ),
        "set": lambda: set_version(args.version) if args.version else CLIResult(False, "Version required", 1),
        "install": lambda: install_version(
            getattr(args, "version", None),
            getattr(args, "from_url", None),
            getattr(args, "force", False),
            not getattr(args, "non_interactive", False)
        ),
        "upgrade": lambda: upgrade_cli(getattr(args, "version", None)),
        "purge": lambda: uninstall_version(
            getattr(args, "version", None),
            False,
            getattr(args, "yes", False),
        ),
        "purge-all": lambda: uninstall_version(
            None,
            True,
            getattr(args, "yes", False),
        ),
        "repair": lambda: repair_version(getattr(args, "version", None)),
        "logs": lambda: show_version_logs(getattr(args, "version", None), getattr(args, "lines", 20)),
    }

    if not args.versions_cmd:
        return list_versions(False, False)

    handler = cmd_map.get(args.versions_cmd)
    return handler() if handler else CLIResult(False, "Unknown command", 1)
