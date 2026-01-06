"""Uninstall handler for Corplang CLI."""
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

from src.commands.utils.utils import Output, Colors, CLIResult


def detect_os() -> str:
    """Detect the operating system."""
    if sys.platform.startswith("linux"):
        return "linux"
    elif sys.platform == "darwin":
        return "macos"
    elif sys.platform in ("win32", "cygwin", "msys"):
        return "windows"
    return "unknown"


def get_shell_config_files() -> List[Path]:
    """Get shell configuration files to check."""
    home = Path.home()
    configs = []
    
    if detect_os() in ("linux", "macos"):
        possible_configs = [
            home / ".bashrc",
            home / ".bash_profile",
            home / ".zshrc",
            home / ".zprofile",
            home / ".profile",
            home / ".config" / "fish" / "config.fish",
        ]
        configs = [cfg for cfg in possible_configs if cfg.exists()]
    
    elif detect_os() == "windows":
        # Windows PowerShell profile
        possible_configs = [
            Path(os.environ.get("USERPROFILE", home)) / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1",
            Path(os.environ.get("USERPROFILE", home)) / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1",
        ]
        configs = [cfg for cfg in possible_configs if cfg.exists()]
    
    return configs


def remove_from_shell_config(config_file: Path) -> Tuple[bool, str]:
    """Remove Corplang-related entries from shell config file."""
    try:
        content = config_file.read_text(encoding="utf-8")
        original = content
        
        # Remove lines containing Corplang references
        lines = content.split("\n")
        filtered = []
        skip_next = False
        
        for line in lines:
            # Skip Corplang-related lines
            if any(marker in line for marker in [
                "corplang", "CORPLANG", ".corplang", 
                "mf07-language", "MF07", "mf --version"
            ]):
                skip_next = True
                continue
            
            # Skip empty lines after Corplang blocks
            if skip_next and line.strip() == "":
                skip_next = False
                continue
            
            skip_next = False
            filtered.append(line)
        
        new_content = "\n".join(filtered)
        
        # Only write if something changed
        if new_content != original:
            config_file.write_text(new_content, encoding="utf-8")
            return True, f"Cleaned {config_file.name}"
        
        return False, f"No entries found in {config_file.name}"
    
    except Exception as e:
        return False, f"Failed to clean {config_file.name}: {e}"


def remove_symlink(link_path: str) -> Tuple[bool, str]:
    """Remove symlink if it exists."""
    try:
        path = Path(link_path)
        if path.exists() or path.is_symlink():
            if detect_os() in ("linux", "macos") and os.geteuid() != 0:
                # Need sudo for /usr/local/bin
                import subprocess
                result = subprocess.run(
                    ["sudo", "rm", "-f", link_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return True, f"Removed symlink: {link_path}"
                else:
                    return False, f"Failed to remove symlink: {result.stderr}"
            else:
                path.unlink()
                return True, f"Removed symlink: {link_path}"
        
        return False, f"Symlink not found: {link_path}"
    
    except Exception as e:
        return False, f"Error removing symlink: {e}"


def remove_environment_variables() -> List[str]:
    """Get list of environment variables to remove."""
    vars_to_remove = [
        "CORPLANG_ACTIVE_VERSION",
        "CORPLANG_STDLIB_PATH",
        "CORPLANG_HOME",
        "MF_INSTALL_DIR",
        "MF_VERSION",
    ]
    
    found = []
    for var in vars_to_remove:
        if os.environ.get(var):
            found.append(var)
    
    return found


def remove_installation_directory(install_dir: Path, force: bool = False) -> Tuple[bool, str]:
    """Remove Corplang installation directory."""
    try:
        if not install_dir.exists():
            return False, f"Installation directory not found: {install_dir}"
        
        if not force:
            # Safety check
            expected_subdirs = ["versions", "bin", "cache"]
            has_expected = any((install_dir / subdir).exists() for subdir in expected_subdirs)
            
            if not has_expected:
                return False, f"Directory doesn't look like a Corplang installation: {install_dir}"
        
        # Remove directory recursively
        shutil.rmtree(install_dir)
        return True, f"Removed installation directory: {install_dir}"
    
    except PermissionError:
        return False, f"Permission denied. Try running with sudo."
    except Exception as e:
        return False, f"Error removing directory: {e}"


def handle_uninstall(args) -> CLIResult:
    """Handle the uninstall command."""
    Output.info("Corplang Uninstaller")
    Output.info("=" * 50)
    print()
    
    # Get installation directory
    install_dir = Path(os.environ.get("MF_INSTALL_DIR", Path.home() / ".corplang"))
    
    # Confirm uninstallation
    if not args.yes:
        Output.warning(f"This will remove Corplang from your system:")
        print(f"  • Installation directory: {install_dir}")
        print(f"  • Symlinks in /usr/local/bin (Linux/macOS)")
        print(f"  • Shell configuration entries")
        print(f"  • Environment variables")
        print()
        
        try:
            response = input("Continue? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                return CLIResult(success=False, message="Uninstallation cancelled by user", exit_code=0)
        except (KeyboardInterrupt, EOFError):
            print()
            return CLIResult(success=False, message="Uninstallation cancelled", exit_code=0)
    
    print()
    Output.step("Removing Corplang components...")
    print()
    
    results = []
    errors = []
    
    # 1. Remove symlinks
    if detect_os() in ("linux", "macos"):
        Output.info("Checking for symlinks...")
        symlinks = ["/usr/local/bin/mf", "/usr/local/bin/corplang"]
        for symlink in symlinks:
            success, msg = remove_symlink(symlink)
            if success:
                Output.success(f"  ✓ {msg}")
                results.append(msg)
            elif "not found" not in msg.lower():
                Output.warning(f"  ⚠ {msg}")
                errors.append(msg)
        print()
    
    # 2. Clean shell configurations
    Output.info("Cleaning shell configuration files...")
    configs = get_shell_config_files()
    if configs:
        for config in configs:
            success, msg = remove_from_shell_config(config)
            if success:
                Output.success(f"  ✓ {msg}")
                results.append(msg)
            else:
                Output.info(f"  • {msg}")
        print()
    else:
        Output.info("  No shell config files found")
        print()
    
    # 3. Remove installation directory
    Output.info("Removing installation directory...")
    success, msg = remove_installation_directory(install_dir, args.force)
    if success:
        Output.success(f"  ✓ {msg}")
        results.append(msg)
    else:
        Output.error(f"  ✗ {msg}")
        errors.append(msg)
    print()
    
    # 4. List environment variables to remove
    env_vars = remove_environment_variables()
    if env_vars:
        Output.warning("Environment variables detected (remove manually if needed):")
        for var in env_vars:
            value = os.environ.get(var, "")
            print(f"  • {var}={value}")
        print()
    
    # 5. Print summary
    Output.info("Uninstallation Summary")
    Output.info("=" * 50)
    
    if results:
        Output.success(f"Successfully removed {len(results)} component(s)")
        for result in results:
            print(f"  ✓ {result}")
        print()
    
    if errors:
        Output.warning(f"Failed to remove {len(errors)} component(s)")
        for error in errors:
            print(f"  ✗ {error}")
        print()
    
    # Final steps
    Output.info("Next steps:")
    print("  1. Restart your shell or terminal")
    
    if detect_os() in ("linux", "macos"):
        print("  2. Verify removal:")
        print("     which mf  # Should return nothing")
        print()
        
        if env_vars:
            print("  3. To remove environment variables, edit your shell config:")
            for config in configs:
                print(f"     {config}")
            print()
    
    elif detect_os() == "windows":
        print("  2. Remove PATH entry manually via:")
        print("     System Settings > Environment Variables")
        print()
    
    if errors:
        return CLIResult(
            success=False,
            message="Uninstallation completed with some errors",
            exit_code=1
        )
    
    return CLIResult(
        success=True,
        message="Corplang has been successfully uninstalled",
        exit_code=0
    )
