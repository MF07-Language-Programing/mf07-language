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
INSTALL_DIR="${MF_INSTALL_DIR:-$HOME/.mf}"
BIN_DIR="$INSTALL_DIR/bin"
VERSION="${MF_VERSION:-latest}"

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
    
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi
    
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        missing+=("pip")
    fi
    
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
                        python3)
                            $SUDO_CMD apt install -y python3 python3-venv 2>/dev/null || log_warning "Failed to install python3"
                            ;;
                        pip)
                            $SUDO_CMD apt install -y python3-pip 2>/dev/null || log_warning "Failed to install pip"
                            ;;
                        git)
                            $SUDO_CMD apt install -y git 2>/dev/null || log_warning "Failed to install git"
                            ;;
                    esac
                done
                
                # Recheck after installation
                missing=()
                if ! command -v python3 &> /dev/null; then
                    missing+=("python3")
                fi
                if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
                    missing+=("pip")
                fi
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
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip git"
        echo "  macOS: brew install python3 git"
        echo "  Windows: Install Git Bash and Python from official sites"
        exit 1
    fi
}

get_latest_version() {
    log_step "Fetching latest version..."
    
    local api_url="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"
    
    if command -v curl &> /dev/null; then
        VERSION=$(curl -fsSL "$api_url" | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
    elif command -v wget &> /dev/null; then
        VERSION=$(wget -qO- "$api_url" | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
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
    
    # Use pip3 if available, otherwise pip
    local pip_cmd="pip3"
    if ! command -v pip3 &> /dev/null; then
        pip_cmd="pip"
    fi
    
    # Always use 'python3 -m pip' (not pip3)
    python3 -m pip install --user -e . || {
        log_error "Installation failed"
        exit 1
    }
    
    cd - > /dev/null
    rm -rf "$tmp_dir"
    
    log_info "Installed mf07-language $VERSION"
}

setup_binary_symlink() {
    log_step "Setting up CLI binary..."
    
    mkdir -p "$BIN_DIR"
    
    local python_bin_dir
    python_bin_dir=$(python3 -c "import site; print(site.USER_BASE + '/bin')")
    
    if [ -f "$python_bin_dir/mf" ]; then
        ln -sf "$python_bin_dir/mf" "$BIN_DIR/mf" 2>/dev/null || {
            cp "$python_bin_dir/mf" "$BIN_DIR/mf"
            chmod +x "$BIN_DIR/mf"
        }
        log_info "CLI binary linked to $BIN_DIR/mf"
    else
        log_warn "CLI binary not found at $python_bin_dir/mf"
    fi
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
        log_info "Added $BIN_DIR to PATH in $shell_profile"
    else
        log_info "PATH already configured in $shell_profile"
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
    echo "     ${GREEN}source ~/.bashrc${RESET}  # or ~/.zshrc, ~/.bash_profile"
    echo ""
    echo "  2. Verify installation:"
    echo "     ${GREEN}mf --version${RESET}"
    echo ""
    echo "  3. Create your first project:"
    echo "     ${GREEN}mf init myproject${RESET}"
    echo "     ${GREEN}cd myproject${RESET}"
    echo "     ${GREEN}mf run main.mp${RESET}"
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
