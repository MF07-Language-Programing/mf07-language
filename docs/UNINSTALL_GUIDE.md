# Corplang Uninstallation Guide

## Overview

Corplang provides multiple ways to completely uninstall from your system, removing:
- CLI binary and versions
- Installation directories
- Symlinks
- Shell configuration entries
- Environment variables

## Methods

### Method 1: Using CLI Command (Recommended)

If you have Corplang installed and the `mf` command is available:

```bash
mf uninstall
```

**Options:**
- `--yes, -y`: Skip confirmation prompt
- `--force, -f`: Force removal even if directory structure looks unexpected

**Example:**
```bash
# Interactive uninstall with confirmation
mf uninstall

# Non-interactive uninstall
mf uninstall --yes

# Force removal
mf uninstall --yes --force
```

### Method 2: Using Standalone Script

If the CLI is broken or you can't access the `mf` command:

```bash
# Download and run
curl -fsSL https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/uninstall.sh | bash

# Or download first, then run
wget https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/uninstall.sh
chmod +x uninstall.sh
./uninstall.sh
```

**Options:**
```bash
./uninstall.sh --yes         # Skip confirmation
./uninstall.sh --force       # Force removal
./uninstall.sh --help        # Show help
```

### Method 3: Manual Uninstallation

If automated methods fail, follow these steps:

#### Linux & macOS

1. **Remove installation directory:**
   ```bash
   rm -rf ~/.corplang
   ```

2. **Remove symlinks:**
   ```bash
   sudo rm -f /usr/local/bin/mf
   sudo rm -f /usr/local/bin/corplang
   ```

3. **Clean shell configurations:**
   ```bash
   # Edit your shell config file
   nano ~/.bashrc  # or ~/.zshrc, ~/.bash_profile, etc.
   
   # Remove lines containing:
   # - corplang
   # - CORPLANG
   # - .corplang
   # - mf07-language
   ```

4. **Restart shell:**
   ```bash
   source ~/.bashrc  # or restart terminal
   ```

#### Windows

1. **Remove installation directory:**
   ```powershell
   Remove-Item -Recurse -Force "$env:USERPROFILE\.corplang"
   ```

2. **Remove from PATH:**
   - Open: System Settings > Environment Variables
   - Edit PATH variable
   - Remove entries containing `.corplang` or `mf07-language`

3. **Clean PowerShell profile (if exists):**
   ```powershell
   notepad $PROFILE
   # Remove Corplang-related lines
   ```

4. **Restart PowerShell**

## What Gets Removed

### Directories
- `~/.corplang/` - Main installation directory
  - `~/.corplang/versions/` - Installed versions
  - `~/.corplang/bin/` - Binary files
  - `~/.corplang/cache/` - Cache files
  - `~/.corplang/mf` - CLI executable

### Symlinks (Linux/macOS)
- `/usr/local/bin/mf`
- `/usr/local/bin/corplang`

### Shell Configuration Files
Entries removed from:
- `~/.bashrc`
- `~/.bash_profile`
- `~/.zshrc`
- `~/.zprofile`
- `~/.profile`
- `~/.config/fish/config.fish`

### Environment Variables
- `CORPLANG_ACTIVE_VERSION`
- `CORPLANG_STDLIB_PATH`
- `CORPLANG_HOME`
- `MF_INSTALL_DIR`
- `MF_VERSION`

## Verification

After uninstallation, verify removal:

```bash
# Check if command exists
which mf
# Should return: nothing (or "mf not found")

# Check if directory exists
ls ~/.corplang
# Should return: "No such file or directory"

# Check environment variables
env | grep CORPLANG
# Should return: nothing
```

## Troubleshooting

### Permission Denied

If you get permission errors:

```bash
# Linux/macOS: Use sudo
sudo mf uninstall

# Or for symlinks:
sudo rm -f /usr/local/bin/mf
```

### Directory Not Empty

If removal fails due to "directory not empty":

```bash
# Force removal
mf uninstall --force

# Or manual removal
rm -rf ~/.corplang
```

### Symlink Removal Fails

```bash
# Check if you have permissions
ls -la /usr/local/bin/mf

# Remove manually with sudo
sudo rm -f /usr/local/bin/mf
```

### Environment Variables Still Set

Environment variables persist in your current shell. They will be cleared when you:
- Restart your terminal
- Open a new terminal window
- Run: `source ~/.bashrc` (or your shell config)

To clear immediately:
```bash
unset CORPLANG_ACTIVE_VERSION
unset CORPLANG_STDLIB_PATH
unset CORPLANG_HOME
unset MF_INSTALL_DIR
unset MF_VERSION
```

### Shell Config Not Cleaned

If shell config still has Corplang entries:

```bash
# Edit manually
nano ~/.bashrc

# Or use sed to remove
sed -i '/corplang\|CORPLANG\|mf07-language/d' ~/.bashrc
```

## Reinstallation

After uninstallation, to reinstall Corplang:

```bash
curl -fsSL https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/install.sh | bash
```

## Support

If you encounter issues during uninstallation:

1. Check [GitHub Issues](https://github.com/MF07-Language-Programing/mf07-language/issues)
2. Try manual uninstallation steps above
3. Report bugs with detailed error messages

## Platform-Specific Notes

### Linux
- Requires `sudo` for `/usr/local/bin` symlink removal
- Supports automatic shell config cleanup
- Works with bash, zsh, fish shells

### macOS
- Same as Linux
- May require macOS Gatekeeper approval for scripts
- Homebrew installations may need special handling

### Windows
- Use Git Bash or PowerShell
- PATH removal requires manual System Settings access
- PowerShell profile cleanup may be needed

## Safety Features

The uninstaller includes safety checks:

1. **Confirmation prompt** - Asks before removing (use `--yes` to skip)
2. **Directory validation** - Checks if directory looks like Corplang installation
3. **Backup creation** - Creates backups of shell config files
4. **Error handling** - Reports failures and suggests manual steps

To bypass safety checks:
```bash
mf uninstall --yes --force
```

⚠️ **Warning:** Use `--force` with caution. It will remove directories even if they don't match expected structure.
