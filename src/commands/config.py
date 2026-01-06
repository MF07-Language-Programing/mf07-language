import json
import os
import subprocess
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml


class CorplangConfig:
    """Configuration with cli-level"""

    VERSION = "1.1.2"
    CACHE_DIR = ".corplang-cache"
    MANIFEST_FILE = "manifest.json"
    CONFIG_FILE = "language_config.yaml"

    @staticmethod
    def get_project_root(start_path: str = ".") -> Optional[Path]:
        """Find the project root by looking for language_config.yaml or manifest.json."""
        current = Path(start_path).resolve()
        
        # If start_path is a file, start from its parent directory
        if current.is_file():
            current = current.parent
        
        for _ in range(10):
            if (current / CorplangConfig.CONFIG_FILE).exists() or \
                    (current / CorplangConfig.MANIFEST_FILE).exists():
                return current
            if current.parent == current:
                break
            current = current.parent
        return None

    @staticmethod
    def get_corplang_home() -> Path:
        """Get Corplang home directory (~/.corplang)."""
        home = Path.home() / ".corplang"
        home.mkdir(exist_ok=True, parents=True)
        return home

    @staticmethod
    def get_installed_versions_dir() -> Path:
        """Get directory where installed versions are stored."""
        versions_dir = CorplangConfig.get_corplang_home() / "versions"
        versions_dir.mkdir(exist_ok=True, parents=True)
        return versions_dir

    @staticmethod
    def get_cache_dir(project_root: Optional[Path] = None) -> Path:
        """Get cache directory for compiled modules."""
        if project_root:
            cache_dir = project_root / CorplangConfig.CACHE_DIR
        else:
            cache_dir = CorplangConfig.get_corplang_home() / "cache"
        cache_dir.mkdir(exist_ok=True, parents=True)
        return cache_dir

    @staticmethod
    def resolve_file_path(file_path: str, project_root: Optional[Path] = None) -> Path:
        """Resolve file path relative to project root or current directory."""
        path = Path(file_path)
        if path.is_absolute():
            return path

        if project_root and (project_root / path).exists():
            return project_root / path

        if Path(file_path).exists():
            return Path(file_path).resolve()

        if project_root:
            return (project_root / path).resolve()

        return path.resolve()

    @staticmethod
    def resolve_module_search_paths(project_root: Optional[Path] = None) -> list[Path]:
        """Get module search paths in order of priority."""
        paths = []

        if project_root:
            paths.extend([
                project_root,
                project_root / "lib",
                project_root / "src",
                project_root / "modules",
            ])

        paths.extend([
            Path.cwd(),
            Path.cwd() / "lib",
            Path.cwd() / "src",
        ])

        stdlib_path = Path(__file__).parent.parent / "corplang" / "stdlib"
        if stdlib_path.exists():
            paths.append(stdlib_path)

        return [p for p in paths if p.exists()]

    @staticmethod
    def load_language_config(project_root: Optional[Path] = None) -> dict:
        """Load language_config.yaml if it exists."""
        if not project_root:
            project_root = CorplangConfig.get_project_root()
        if not project_root:
            return {}

        config_file = project_root / CorplangConfig.CONFIG_FILE
        if not config_file.exists():
            return {}

        with open(config_file) as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def is_corplang_file(file_path: str) -> bool:
        """Check if a file is a Corplang source file."""
        return file_path.endswith((".mp", ".mf"))


class VersionManager:
    """Manages installed versions with integrity validation and remote capabilities."""

    DEFAULT_REPO = "MF07-Language-Programing/mf07-language"

    def __init__(self):
        self.versions_dir = CorplangConfig.get_installed_versions_dir()
        self.log_file = CorplangConfig.get_corplang_home() / "version_manager.log"
        self._version_cache = {}

    def log_action(self, action: str, version: str, status: str, details: str = ""):
        """Log version manager actions."""
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {action:15} | {version:10} | {status:10} | {details}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def fetch_remote_releases(self, repo: str = None) -> List[Dict[str, Any]]:
        """Fetch releases from GitHub repository."""
        repo = repo or self.DEFAULT_REPO
        releases = []

        # noinspection PyBroadException
        try:
            url = f"https://api.github.com/repos/{repo}/releases"
            headers = {"Accept": "application/vnd.github+json"}

            token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
            if token:
                headers["Authorization"] = f"token {token}"

            response = subprocess.run(
                ["curl", "-s", "-H", f"Accept: application/vnd.github+json", url],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if response.returncode == 0 and response.stdout:
                data = json.loads(response.stdout)
                if isinstance(data, list):
                    for release in data[:20]:
                        assets = release.get("assets", [])
                        asset_list = [{
                            "name": a.get("name", ""),
                            "url": a.get("browser_download_url", ""),
                            "size": a.get("size", 0)
                        } for a in assets]

                        releases.append({
                            "tag_name": release.get("tag_name", ""),
                            "name": release.get("name", ""),
                            "published_at": release.get("published_at", ""),
                            "draft": release.get("draft", False),
                            "prerelease": release.get("prerelease", False),
                            "zipball_url": release.get("zipball_url", ""),
                            "tarball_url": release.get("tarball_url", ""),
                            "assets": asset_list,
                        })
        except Exception:
            pass

        return releases

    def download_version(self, version: str, url: str = None) -> Optional[str]:
        """Download a version from GitHub or custom URL."""
        if not url:
            releases = self.fetch_remote_releases()
            matching = [r for r in releases if
                        r["tag_name"] == version or r["tag_name"].lstrip("v") == version.lstrip("v")]
            if not matching:
                self.log_action("DOWNLOAD", version, "FAILED", "version not found in releases")
                return None

            # Prefer tarball for GitHub releases
            release = matching[0]
            url = release.get("tarball_url") or release.get("download_url")

            if not url:
                self.log_action("DOWNLOAD", version, "FAILED", "no download URL available")
                return None

        target_dir = self.versions_dir / version
        target_dir.mkdir(exist_ok=True, parents=True)

        try:
            self.log_action("DOWNLOAD", version, "STARTED", url)

            if url.startswith("http"):
                archive_file = target_dir / "release.tar.gz"
                cmd = ["curl", "-sL", url, "-o", str(archive_file)]
                result = subprocess.run(cmd, timeout=300, capture_output=True)

                if result.returncode != 0:
                    self.log_action("DOWNLOAD", version, "FAILED", f"curl error: {result.stderr.decode()}")
                    return None

                # Verify file was downloaded and is not empty
                if not archive_file.exists() or archive_file.stat().st_size < 100:
                    self.log_action("DOWNLOAD", version, "FAILED", "downloaded file is empty or too small")
                    return None

                # Extract archive
                extract_cmd = ["tar", "-xzf", str(archive_file), "-C", str(target_dir), "--strip-components=1"]
                extract_result = subprocess.run(extract_cmd, timeout=60, capture_output=True)

                if extract_result.returncode != 0:
                    self.log_action("DOWNLOAD", version, "FAILED",
                                    f"extraction error: {extract_result.stderr.decode()}")
                    return None

                # Clean up archive
                archive_file.unlink(missing_ok=True)

            self.log_action("DOWNLOAD", version, "SUCCESS", str(target_dir))
            return str(target_dir)

        except Exception as e:
            self.log_action("DOWNLOAD", version, "ERROR", str(e))
            return None

    def download_cli_binary(self, version: str, cli_url: str, checksum_url: str | None = None) -> bool:
        """Download CLI binary to global corplang home (~/.corplang)."""
        try:
            platform_suffix = {
                'linux': 'mf',
                'darwin': 'mf',
                'windows': 'mf.exe',
            }[__import__('platform').system().lower()]

            base_dir = CorplangConfig.get_corplang_home()
            cli_file = base_dir / platform_suffix

            cmd = ["curl", "-sL", cli_url, "-o", str(cli_file)]
            result = subprocess.run(cmd, timeout=300, capture_output=True)

            if result.returncode != 0:
                return False

            if not (cli_file.exists() and cli_file.stat().st_size > 1000):
                return False

            cli_file.chmod(0o755)

            # Optionally download checksum manifest
            if checksum_url:
                checksum_file = base_dir / f"{platform_suffix}.sha256"
                subprocess.run(["curl", "-sL", checksum_url, "-o", str(checksum_file)], timeout=60)

            self.log_action("CLI_DOWNLOAD", version, "SUCCESS", str(cli_file))
            return True
        except Exception as e:
            self.log_action("CLI_DOWNLOAD", version, "ERROR", str(e))
            return False

    def configure_cli_environment(self) -> bool:
        """Ensure CLI is globally invocable (PATH/shim), cross-platform best-effort."""
        try:
            home = CorplangConfig.get_corplang_home()
            platform_suffix = {
                'linux': 'mf',
                'darwin': 'mf',
                'windows': 'mf.exe',
            }[__import__('platform').system().lower()]
            cli_path = home / platform_suffix
            if not cli_path.exists():
                return False

            system = __import__('platform').system().lower()

            if system in {"linux", "darwin"}:
                # Create ~/.local/bin symlink for PATH-friendly location
                local_bin = Path.home() / ".local" / "bin"
                local_bin.mkdir(parents=True, exist_ok=True)
                shim = local_bin / "mf"
                if shim.exists() or shim.is_symlink():
                    try:
                        shim.unlink()
                    except Exception:
                        pass
                try:
                    shim.symlink_to(cli_path)
                except FileExistsError:
                    pass

                # Ensure executable bit
                cli_path.chmod(cli_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

                # Append PATH export to common shells if missing
                export_line = "export PATH=\"$HOME/.local/bin:$PATH\"  # corplang-cli"
                for rc in [Path.home() / ".bashrc", Path.home() / ".zshrc"]:
                    try:
                        if rc.exists():
                            content = rc.read_text()
                            if "corplang-cli" not in content:
                                with rc.open("a") as f:
                                    f.write(f"\n{export_line}\n")
                        else:
                            with rc.open("w") as f:
                                f.write(f"{export_line}\n")
                    except Exception:
                        pass

            elif system == "windows":
                # Create cmd shim in corplang home
                shim = home / "mf.cmd"
                shim.write_text(f"@echo off\n\"{cli_path}\" %*\n")

                # Add corplang home to user PATH using setx (best effort)
                try:
                    subprocess.run([
                        "setx", "PATH", f"%PATH%;{str(home)}"
                    ], check=False, capture_output=True, text=True)
                except Exception:
                    pass

            self.log_action("CLI_ENV", cli_path.name, "SUCCESS", str(cli_path))
            return True
        except Exception as e:
            self.log_action("CLI_ENV", "unknown", "ERROR", str(e))
            return False

    def uninstall_version(self, version: str) -> bool:
        """Remove a specific installed version."""
        if version == "local":
            return False

        target = self.versions_dir / version
        if not target.exists() or not target.is_dir():
            return False

        try:
            shutil.rmtree(target)
            self.log_action("UNINSTALL", version, "SUCCESS", str(target))

            # Clear active version if it was this one
            if os.environ.get("CORPLANG_ACTIVE_VERSION") == version:
                os.environ.pop("CORPLANG_ACTIVE_VERSION", None)

            return True
        except Exception as e:
            self.log_action("UNINSTALL", version, "ERROR", str(e))
            return False

    def uninstall_all_versions(self) -> int:
        """Remove all installed versions (keeps global CLI and logs)."""
        removed = 0
        for entry in list(self.versions_dir.iterdir()) if self.versions_dir.exists() else []:
            if entry.is_dir():
                try:
                    shutil.rmtree(entry)
                    removed += 1
                    self.log_action("UNINSTALL", entry.name, "SUCCESS", str(entry))
                except Exception as e:
                    self.log_action("UNINSTALL", entry.name, "ERROR", str(e))
        return removed

    def get_version_logs(self, version: str = None, limit: int = 50) -> List[str]:
        """Get logs for a specific version or all actions."""
        if not self.log_file.exists():
            return []

        # noinspection PyBroadException
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()

            if version:
                lines = [l for l in lines if version in l]

            return lines[-limit:]
        except Exception:
            return []

    def print_version_logs(self, version: str = None):
        """Print formatted version logs."""
        logs = self.get_version_logs(version)
        if not logs:
            return

        from src.commands.utils.utils import Output
        Output.section("Version Logs")
        for log in logs:
            Output.print(log.strip())

    def list_versions(self, detailed: bool = False) -> Dict[str, Dict[str, Any]]:
        """List all installed versions."""
        versions = {}
        repo_root = Path(__file__).parent.parent.parent

        if (repo_root / "src" / "corplang").exists():
            versions["local"] = {
                "path": str(repo_root),
                "valid": True,
                "type": "development",
                "description": "Development environment",
                "installed_at": datetime.now().isoformat(),
            }
        if self.versions_dir.exists():
            for version_dir in self.versions_dir.iterdir():
                if version_dir.is_dir():
                    version_name = version_dir.name
                    versions[version_name] = {
                        "path": str(version_dir),
                        "valid": self._validate_version(str(version_dir)),
                        "type": "installed",
                        "description": f"Version {version_name}",
                        "installed_at": datetime.fromtimestamp(version_dir.stat().st_mtime).isoformat(),
                    }

        return versions

    @staticmethod
    def _validate_version(path: str) -> bool:
        """Check if the version installation is valid."""
        base = Path(path)

        required = (
            "src/corplang/compiler/lexer.py",
        )

        parser_options = (
            "src/corplang/compiler/parser.py",
            "src/corplang/compiler/legacy.py",
            "src/corplang/compiler/parser_legacy.py",
        )

        if not all((base / f).exists() for f in required):
            return False

        if not any((base / f).exists() for f in parser_options):
            return False

        return True

    @staticmethod
    def get_active_version() -> Optional[str]:
        """Get an active version from env or config."""
        active = os.environ.get("CORPLANG_ACTIVE_VERSION")
        if active:
            return active

        project_root = CorplangConfig.get_project_root()
        if project_root:
            config = CorplangConfig.load_language_config(project_root)
            return config.get("corplang", {}).get("version")

        return "local"

    def set_active_version(self, version: str) -> bool:
        """Set the active version."""
        versions = self.list_versions()
        if version not in versions:
            return False

        os.environ["CORPLANG_ACTIVE_VERSION"] = version
        self.log_action("SET_ACTIVE", version, "SUCCESS")

        project_root = CorplangConfig.get_project_root()
        if project_root:
            try:
                config = CorplangConfig.load_language_config(project_root)
                config.setdefault("corplang", {})["version"] = version

                import yaml
                config_file = project_root / "language_config.yaml"
                with open(config_file, "w") as f:
                    yaml.dump(config, f)
                return True
            except Exception:
                pass

        return True


class ConfigManager:
    """Manages eco.system.json and language_config.yaml."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or CorplangConfig.get_project_root() or Path.cwd()
        self.eco_system_path = self.project_root / "eco.system.json"
        self.language_config_path = self.project_root / "language_config.yaml"

    def load_eco_system(self) -> Dict[str, Any]:
        """Load eco.system.json."""
        if not self.eco_system_path.exists():
            return {}
        try:
            with open(self.eco_system_path) as f:
                return json.load(f)
        except Exception:
            return {}

    def load_language_config(self) -> Dict[str, Any]:
        """Load language_config.yaml."""
        if not self.language_config_path.exists():
            return {}
        try:
            import yaml
            with open(self.language_config_path) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def save_eco_system(self, data: Dict[str, Any]) -> bool:
        """Save eco.system.json."""
        try:
            self.eco_system_path.parent.mkdir(exist_ok=True, parents=True)
            with open(self.eco_system_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def save_language_config(self, data: Dict[str, Any]) -> bool:
        """Save language_config.yaml."""
        try:
            import yaml
            self.language_config_path.parent.mkdir(exist_ok=True, parents=True)
            with open(self.language_config_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
            return True
        except Exception:
            return False

    def validate(self) -> Dict[str, Any]:
        """Validate both configuration files."""
        eco = self.load_eco_system()
        lang = self.load_language_config()

        issues = []
        if not eco:
            issues.append("eco.system.json is missing or empty")
        if not lang:
            issues.append("language_config.yaml is missing or empty")

        eco_version = eco.get("corplang", {}).get("version")
        lang_version = lang.get("corplang", {}).get("version")
        if eco_version and lang_version and eco_version != lang_version:
            issues.append(f"Version mismatch: eco={eco_version}, lang={lang_version}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "has_eco": bool(eco),
            "has_language_config": bool(lang),
        }

    def sync(self) -> bool:
        """Synchronize configurations."""
        eco = self.load_eco_system()
        lang = self.load_language_config()

        if not eco:
            eco = self._default_eco_system()
        if not lang:
            lang = self._default_language_config()

        eco_version = eco.get("corplang", {}).get("version")
        lang_version = lang.get("corplang", {}).get("version")

        if not lang_version and eco_version:
            lang.setdefault("corplang", {})["version"] = eco_version
        elif not eco_version and lang_version:
            eco.setdefault("corplang", {})["version"] = lang_version

        return self.save_eco_system(eco) and self.save_language_config(lang)

    @staticmethod
    def _default_eco_system() -> Dict[str, Any]:
        return {
            "corplang": {
                "version": "0.1.0",
                "environment": "development",
            }
        }

    @staticmethod
    def _default_language_config() -> Dict[str, Any]:
        return {
            "corplang": {
                "version": "0.1.0",
                "name": "corplang-project",
            }
        }

