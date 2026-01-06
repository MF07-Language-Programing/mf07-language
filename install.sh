#!/usr/bin/env bash
#
# MF07 Language Installer
# Compatible with: Linux, macOS, Windows (Git Bash/WSL)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/<owner>/<repo>/main/install.sh | bash
#   wget -qO- https://raw.githubusercontent.com/<owner>/<repo>/main/install.sh | bash
#

set -e

REPO_OWNER="${MF_REPO_OWNER:-MF07-Language-Programing}"
REPO_NAME="${MF_REPO_NAME:-mf07-language}"
INSTALL_DIR="${MF_INSTALL_DIR:-$HOME/.corplang}"
BIN_DIR="$INSTALL_DIR/bin"
VERSION="${MF_VERSION:-latest}"
PYTHON_CMD=""

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

log_info() {
    echo -e "${GREEN}[INFO]${RESET} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${RESET} $1"
}

# Backward compatibility: some cached scripts may call log_warning
log_warning() {
    log_warn "$1"
}

log_error() {
    echo -e "${RED}[ERROR]${RESET} $1"
}

log_step() {
    echo -e "${BOLD}==>${RESET} $1"
}

detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW*|MSYS*) echo "windows";;
        *)          echo "unknown";;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64)   echo "x64";;
        aarch64|arm64)  echo "arm64";;
        *)              echo "unknown";;
    esac
}

check_dependencies() {
    local missing=()

    ensure_python

    if ! command -v git &> /dev/null; then
        missing+=("git")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        # Try to auto-install on Linux with apt
        if [ "$(detect_os)" = "linux" ] && command -v apt &> /dev/null && command -v sudo &> /dev/null; then
            log_info "Missing dependencies: ${missing[*]}"
            log_info "Attempting to install automatically (sudo may ask for password)..."
            
            # Use sudo if not root
            local SUDO_CMD=""
            if [ "$(id -u)" -ne 0 ]; then
                SUDO_CMD="sudo"
                log_info "Running: sudo apt update && sudo apt install -y ${missing[*]}"
            fi
            
            if $SUDO_CMD apt update -qq 2>/dev/null; then
                for dep in "${missing[@]}"; do
                    case "$dep" in
                        git)
                            $SUDO_CMD apt install -y git 2>/dev/null || log_warn "Failed to install git"
                            ;;
                    esac
                done
                
                # Recheck after installation
                missing=()
                if ! command -v git &> /dev/null; then
                    missing+=("git")
                fi
                
                if [ ${#missing[@]} -eq 0 ]; then
                    log_info "Dependencies installed successfully!"
                    return 0
                fi
            fi
        fi
        
        # If auto-install failed or not available, show manual instructions
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Install them manually:"
        echo "  Ubuntu/Debian: sudo apt install python3.14 python3.14-venv python3.14-distutils git"
        echo "  macOS: brew install python3 git"
        echo "  Windows: Install Git Bash and Python from official sites"
        exit 1
    fi
}

ensure_python() {
    local desired="python3.14"

    if command -v "$desired" >/dev/null 2>&1; then
        PYTHON_CMD="$desired"
    fi

    if [ -z "$PYTHON_CMD" ] && [ "$(detect_os)" = "linux" ] && command -v apt >/dev/null 2>&1; then
        log_warn "python3.14 not found. Attempting to install automatically..."
        local SUDO_CMD=""
        if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
            SUDO_CMD="sudo"
            log_info "Running: sudo apt update && sudo apt install -y python3.14 python3.14-venv python3.14-distutils"
        fi
        $SUDO_CMD apt update -qq >/dev/null 2>&1 || true
        $SUDO_CMD apt install -y python3.14 python3.14-venv python3.14-distutils >/dev/null 2>&1 || log_warn "Failed to install python3.14 via apt"
        if command -v "$desired" >/dev/null 2>&1; then
            PYTHON_CMD="$desired"
        fi
    fi

    if [ -z "$PYTHON_CMD" ]; then
        log_warn "Falling back to bundled python3.14 using uv (no sudo)."
        local UV_DIR="$HOME/.local/share/mf07-uv"
        local UV_BIN="$UV_DIR/uv"
        if [ ! -x "$UV_BIN" ]; then
            log_info "Installing uv package manager..."
            local UV_URL="https://astral.sh/uv/install.sh"
            mkdir -p "$UV_DIR"
            if command -v curl >/dev/null 2>&1; then
                curl -fsSL "$UV_URL" | env UV_INSTALL_DIR="$UV_DIR" sh >/dev/null 2>&1 || {
                    log_error "Failed to install uv"
                    exit 1
                }
            elif command -v wget >/dev/null 2>&1; then
                wget -qO- "$UV_URL" | env UV_INSTALL_DIR="$UV_DIR" sh >/dev/null 2>&1 || {
                    log_error "Failed to install uv"
                    exit 1
                }
            else
                log_error "curl or wget required to install python3.14 automatically"
                exit 1
            fi
        fi

        if [ -x "$UV_BIN" ]; then
            log_info "Downloading python3.14 (this may take a moment)..."
            local UV_PYTHON_DIR="$UV_DIR/python"
            mkdir -p "$UV_PYTHON_DIR"
            UV_PYTHON_INSTALL_DIR="$UV_PYTHON_DIR" "$UV_BIN" python install 3.14 >/dev/null 2>&1 || {
                log_error "Failed to install python3.14 via uv"
                exit 1
            }
            PYTHON_CMD=$("$UV_BIN" python find 3.14 2>/dev/null | head -1)
            if [ -z "$PYTHON_CMD" ] || [ ! -x "$PYTHON_CMD" ]; then
                log_error "Failed to locate python3.14 after uv installation"
                exit 1
            fi
            log_info "Python3.14 provisioned at $PYTHON_CMD"
        else
            log_error "uv installer failed; cannot provision python3.14"
            exit 1
        fi
    fi

    if [ -z "$PYTHON_CMD" ]; then
        log_error "python3.14 is required but not available. Please install python3.14 and rerun."
        exit 1
    fi

    local py_ver
    py_ver=$("$PYTHON_CMD" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
    )

    if [ "$py_ver" != "3.14" ]; then
        log_error "Expected python3.14, but found $py_ver"
        exit 1
    fi

    if ! "$PYTHON_CMD" -Im ensurepip --version >/dev/null 2>&1; then
        if [ "$(detect_os)" = "linux" ] && command -v apt >/dev/null 2>&1; then
            log_warn "ensurepip missing for python3.14. Installing python3.14-venv..."
            local SUDO_CMD=""
            if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
                SUDO_CMD="sudo"
            fi
            $SUDO_CMD apt install -y python3.14-venv python3.14-distutils >/dev/null 2>&1 || log_warn "Failed to install python3.14-venv"
        fi

        if ! "$PYTHON_CMD" -Im ensurepip --upgrade >/dev/null 2>&1; then
            log_error "ensurepip is unavailable for $PYTHON_CMD. Please install python3.14-venv."
            exit 1
        fi
    else
        "$PYTHON_CMD" -Im ensurepip --upgrade >/dev/null 2>&1 || true
    fi
}

get_latest_version() {
    log_step "Fetching latest version..."
    
    local OS="$(detect_os)"
    local platform_suffix=""
    case "$OS" in
        linux)   platform_suffix="-linux" ;;
        macos)   platform_suffix="-macos" ;;
        windows) platform_suffix="-windows" ;;
    esac
    
    local api_url="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases"
    
    if command -v curl &> /dev/null; then
        # Get all releases and filter by platform using python for robust JSON parsing
        VERSION=$(curl -fsSL "$api_url" 2>/dev/null | "$PYTHON_CMD" -c "
import sys, json
try:
    releases = json.load(sys.stdin)
    suffix = '$platform_suffix'
    for r in releases:
        tag = r.get('tag_name', '')
        if tag.endswith(suffix):
            print(tag.lstrip('v'))
            break
except: pass
" 2>/dev/null)
    elif command -v wget &> /dev/null; then
        VERSION=$(wget -qO- "$api_url" 2>/dev/null | "$PYTHON_CMD" -c "
import sys, json
try:
    releases = json.load(sys.stdin)
    suffix = '$platform_suffix'
    for r in releases:
        tag = r.get('tag_name', '')
        if tag.endswith(suffix):
            print(tag.lstrip('v'))
            break
except: pass
" 2>/dev/null)
    else
        log_error "curl or wget required"
        exit 1
    fi
    
    if [ -z "$VERSION" ]; then
        log_warn "Failed to fetch version from API, using fallback"
        VERSION="0.1.0"
    fi
    
    log_info "Target version: $VERSION"
}

install_via_pip() {
    log_step "Installing mf07-language from source..."
    
    local tmp_dir=$(mktemp -d)
    cd "$tmp_dir"
    
    local repo_url="https://github.com/$REPO_OWNER/$REPO_NAME"
    
    if [ "$VERSION" = "latest" ]; then
        log_info "Cloning main branch..."
        git clone --depth 1 "$repo_url.git" mf07 || {
            log_error "Failed to clone repository"
            exit 1
        }
    else
        log_info "Downloading version $VERSION..."
        if command -v curl &> /dev/null; then
            curl -fsSL "$repo_url/archive/refs/tags/v$VERSION.tar.gz" | tar xz
        elif command -v wget &> /dev/null; then
            wget -qO- "$repo_url/archive/refs/tags/v$VERSION.tar.gz" | tar xz
        else
            log_error "curl or wget required"
            exit 1
        fi
        
        cd "mf07-language-$VERSION" 2>/dev/null || {
            log_error "Failed to extract archive"
            exit 1
        }
    fi
    
    cd mf07* 2>/dev/null || true

    # Run pip as invoking user (when sudo) to avoid system-wide install
    local py_cmd="$PYTHON_CMD"
    local pip_cmd=("$py_cmd" -m pip)
    if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
        pip_cmd=(sudo -u "$SUDO_USER" -E "$py_cmd" -m pip)
    fi

    # Try user install with break-system-packages; fallback to venv if still blocked
    if ! PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_BREAK_SYSTEM_PACKAGES=1 "${pip_cmd[@]}" install --user --break-system-packages -e . 2>/dev/null; then
        if ! PIP_DISABLE_PIP_VERSION_CHECK=1 "${pip_cmd[@]}" install --user -e . 2>/dev/null; then
            log_warn "User install blocked by PEP 668. Falling back to isolated venv with python3.14."
            local VENV_DIR="$HOME/.local/share/mf07-language-venv"

            if ! "$py_cmd" -m venv "$VENV_DIR" >/dev/null 2>&1; then
                log_error "Failed to create venv with python3.14 (ensure python3.14-venv is installed)"
                exit 1
            fi

            # Ensure pip exists even if ensurepip under-delivers
            if [ ! -x "$VENV_DIR/bin/pip" ]; then
                local GET_PIP="$VENV_DIR/get-pip.py"
                if command -v curl >/dev/null 2>&1; then
                    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o "$GET_PIP"
                elif command -v wget >/dev/null 2>&1; then
                    wget -qO "$GET_PIP" https://bootstrap.pypa.io/get-pip.py
                else
                    log_error "curl or wget required to bootstrap pip"
                    exit 1
                fi
                "$VENV_DIR/bin/python" "$GET_PIP" >/dev/null 2>&1 || { log_error "Failed to bootstrap pip"; exit 1; }
                rm -f "$GET_PIP"
            fi

            "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel >/dev/null 2>&1 || true
            "$VENV_DIR/bin/pip" install -e . || { log_error "Venv install failed"; exit 1; }
            mkdir -p "$BIN_DIR"
            ln -sf "$VENV_DIR/bin/mf" "$BIN_DIR/mf"
            log_info "Installed in isolated venv at $VENV_DIR"
            cd - > /dev/null
            rm -rf "$tmp_dir"
            log_info "Installed mf07-language $VERSION"
            return
        fi
    fi
    
    cd - > /dev/null
    rm -rf "$tmp_dir"
    
    log_info "Installed mf07-language $VERSION"
}

setup_binary_symlink() {
    log_step "Setting up CLI binary..."
    
    mkdir -p "$BIN_DIR"
    
    # Check if already installed in venv (from fallback path)
    local VENV_DIR="$HOME/.local/share/mf07-language-venv"
    if [ -f "$VENV_DIR/bin/mf" ]; then
        ln -sf "$VENV_DIR/bin/mf" "$BIN_DIR/mf" 2>/dev/null || {
            cp "$VENV_DIR/bin/mf" "$BIN_DIR/mf"
            chmod +x "$BIN_DIR/mf"
        }
        log_info "✓ CLI executable installed at: $BIN_DIR/mf"
        return
    fi
    
    # Otherwise check user site packages
    local python_bin_dir
    python_bin_dir=$("$PYTHON_CMD" -c "import site; print(site.USER_BASE + '/bin')" 2>/dev/null || echo "")
    
    if [ -n "$python_bin_dir" ] && [ -f "$python_bin_dir/mf" ]; then
        ln -sf "$python_bin_dir/mf" "$BIN_DIR/mf" 2>/dev/null || {
            cp "$python_bin_dir/mf" "$BIN_DIR/mf"
            chmod +x "$BIN_DIR/mf"
        }
        log_info "✓ CLI executable installed at: $BIN_DIR/mf"
        return
    fi
    
    # Create wrapper script as fallback
    log_info "Creating CLI wrapper script..."
    cat > "$BIN_DIR/mf" << EOF
#!/usr/bin/env bash
exec "$PYTHON_CMD" -m src.commands "\$@"
EOF
    chmod +x "$BIN_DIR/mf"
    log_info "✓ CLI executable installed at: $BIN_DIR/mf"
}

setup_shell_profile() {
    log_step "Configuring shell environment..."
    
    local shell_profile
    local shell_name=$(basename "$SHELL")
    
    case "$shell_name" in
        bash)
            if [ "$(detect_os)" = "macos" ]; then
                shell_profile="$HOME/.bash_profile"
            else
                shell_profile="$HOME/.bashrc"
            fi
            ;;
        zsh)
            shell_profile="$HOME/.zshrc"
            ;;
        fish)
            shell_profile="$HOME/.config/fish/config.fish"
            ;;
        *)
            shell_profile="$HOME/.profile"
            ;;
    esac
    
    local path_export="export PATH=\"\$PATH:$BIN_DIR\""
    
    if ! grep -q "$BIN_DIR" "$shell_profile" 2>/dev/null; then
        echo "" >> "$shell_profile"
        echo "# MF07 Language CLI" >> "$shell_profile"
        echo "$path_export" >> "$shell_profile"
        log_info "✓ Environment variables configured successfully"
        log_info "  Added $BIN_DIR to PATH in $shell_profile"
    else
        log_info "✓ Environment variables already configured"
        log_info "  PATH already includes $BIN_DIR in $shell_profile"
    fi
}

verify_installation() {
    log_step "Verifying installation..."
    
    export PATH="$PATH:$BIN_DIR"
    
    if command -v mf &> /dev/null; then
        local installed_version
        installed_version=$(mf --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "unknown")
        log_info "✓ MF CLI installed successfully"
        log_info "  Version: $installed_version"
        log_info "  Path: $(which mf)"
    else
        log_warn "CLI not found in PATH. Restart your shell or run:"
        echo "  export PATH=\"\$PATH:$BIN_DIR\""
    fi
}

cleanup() {
    log_step "Cleaning up..."
    # Future: clean temporary files
}

print_next_steps() {
    echo ""
    echo -e "${BOLD}Installation complete!${RESET}"
    echo ""
    echo "Next steps:"
    echo "  1. Restart your shell or run:"
    echo -e "     ${GREEN}source ~/.bashrc${RESET}  # or ~/.zshrc, ~/.bash_profile"
    echo ""
    echo "  2. Verify installation:"
    echo -e "     ${GREEN}mf --version${RESET}"
    echo ""
    echo "  3. Create your first project:"
    echo -e "     ${GREEN}mf init myproject${RESET}"
    echo -e "     ${GREEN}cd myproject${RESET}"
    echo -e "     ${GREEN}mf run main.mp${RESET}"
    echo ""
    echo "Documentation: https://github.com/$REPO_OWNER/$REPO_NAME"
    echo "Issues: https://github.com/$REPO_OWNER/$REPO_NAME/issues"
    echo ""
}

main() {
    echo -e "${BOLD}MF07 Language Installer${RESET}"
    echo ""
    
    local os=$(detect_os)
    local arch=$(detect_arch)
    
    log_info "Detected OS: $os ($arch)"
    
    if [ "$os" = "unknown" ] || [ "$arch" = "unknown" ]; then
        log_error "Unsupported platform: $os $arch"
        exit 1
    fi
    
    check_dependencies
    
    if [ "$VERSION" = "latest" ]; then
        get_latest_version
    fi
    
    install_via_pip
    setup_binary_symlink
    setup_shell_profile
    verify_installation
    cleanup
    print_next_steps
}

trap 'log_error "Installation failed. Please check the error messages above."' ERR

main "$@"
