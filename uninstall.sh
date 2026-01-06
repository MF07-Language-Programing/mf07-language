#!/usr/bin/env bash
#
# Corplang Uninstaller
# Compatible with: Linux, macOS, Windows (Git Bash/WSL)
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/MF07-Language-Programing/mf07-language/main/uninstall.sh | bash
#   bash uninstall.sh
#   bash uninstall.sh --yes
#

set -e

INSTALL_DIR="${MF_INSTALL_DIR:-$HOME/.corplang}"
FORCE=false
YES=false

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
RESET="\033[0m"

log_info() {
    echo -e "${CYAN}ℹ${RESET} $1"
}

log_success() {
    echo -e "${GREEN}✓${RESET} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${RESET} $1"
}

log_error() {
    echo -e "${RED}✗${RESET} $1"
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

remove_symlinks() {
    log_step "Removing symlinks..."
    
    local os=$(detect_os)
    local removed=0
    
    if [ "$os" = "linux" ] || [ "$os" = "macos" ]; then
        local symlinks=(
            "/usr/local/bin/mf"
            "/usr/local/bin/corplang"
        )
        
        for symlink in "${symlinks[@]}"; do
            if [ -L "$symlink" ] || [ -e "$symlink" ]; then
                if [ "$(id -u)" -ne 0 ] && command -v sudo &> /dev/null; then
                    if sudo rm -f "$symlink" 2>/dev/null; then
                        log_success "Removed: $symlink"
                        ((removed++))
                    else
                        log_warn "Failed to remove: $symlink (may need manual removal)"
                    fi
                elif [ "$(id -u)" -eq 0 ]; then
                    rm -f "$symlink"
                    log_success "Removed: $symlink"
                    ((removed++))
                else
                    log_warn "Cannot remove $symlink (no sudo available)"
                fi
            fi
        done
    fi
    
    if [ $removed -eq 0 ]; then
        log_info "No symlinks found"
    fi
    
    echo ""
}

clean_shell_configs() {
    log_step "Cleaning shell configuration files..."
    
    local configs=()
    local cleaned=0
    
    # Find shell config files
    [ -f "$HOME/.bashrc" ] && configs+=("$HOME/.bashrc")
    [ -f "$HOME/.bash_profile" ] && configs+=("$HOME/.bash_profile")
    [ -f "$HOME/.zshrc" ] && configs+=("$HOME/.zshrc")
    [ -f "$HOME/.zprofile" ] && configs+=("$HOME/.zprofile")
    [ -f "$HOME/.profile" ] && configs+=("$HOME/.profile")
    [ -f "$HOME/.config/fish/config.fish" ] && configs+=("$HOME/.config/fish/config.fish")
    
    if [ ${#configs[@]} -eq 0 ]; then
        log_info "No shell config files found"
        echo ""
        return
    fi
    
    for config in "${configs[@]}"; do
        # Create backup
        cp "$config" "${config}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        
        # Remove Corplang-related lines
        if grep -qE "corplang|CORPLANG|\.corplang|mf07-language|MF07" "$config" 2>/dev/null; then
            sed -i.tmp -E '/corplang|CORPLANG|\.corplang|mf07-language|MF07/d' "$config" 2>/dev/null || \
            sed -i '' -E '/corplang|CORPLANG|\.corplang|mf07-language|MF07/d' "$config" 2>/dev/null || true
            
            # Remove temp file
            rm -f "${config}.tmp" 2>/dev/null || true
            
            log_success "Cleaned: $(basename "$config")"
            ((cleaned++))
        fi
    done
    
    if [ $cleaned -eq 0 ]; then
        log_info "No Corplang entries found in shell configs"
    fi
    
    echo ""
}

remove_installation_dir() {
    log_step "Removing installation directory..."
    
    if [ ! -d "$INSTALL_DIR" ]; then
        log_info "Installation directory not found: $INSTALL_DIR"
        echo ""
        return 1
    fi
    
    # Safety check
    if [ "$FORCE" = false ]; then
        local has_expected=false
        [ -d "$INSTALL_DIR/versions" ] && has_expected=true
        [ -d "$INSTALL_DIR/bin" ] && has_expected=true
        [ -d "$INSTALL_DIR/cache" ] && has_expected=true
        [ -f "$INSTALL_DIR/mf" ] && has_expected=true
        
        if [ "$has_expected" = false ]; then
            log_error "Directory doesn't look like a Corplang installation: $INSTALL_DIR"
            log_info "Use --force to remove anyway"
            echo ""
            return 1
        fi
    fi
    
    # Remove directory
    if rm -rf "$INSTALL_DIR" 2>/dev/null; then
        log_success "Removed: $INSTALL_DIR"
        echo ""
        return 0
    else
        log_error "Failed to remove: $INSTALL_DIR"
        log_info "You may need to remove it manually"
        echo ""
        return 1
    fi
}

list_environment_vars() {
    log_step "Checking environment variables..."
    
    local vars=(
        "CORPLANG_ACTIVE_VERSION"
        "CORPLANG_STDLIB_PATH"
        "CORPLANG_HOME"
        "MF_INSTALL_DIR"
        "MF_VERSION"
    )
    
    local found=0
    
    for var in "${vars[@]}"; do
        if [ -n "${!var}" ]; then
            log_warn "$var=${!var}"
            ((found++))
        fi
    done
    
    if [ $found -eq 0 ]; then
        log_info "No Corplang environment variables detected"
    else
        echo ""
        log_info "These environment variables are still set in your current shell."
        log_info "They will be cleared when you restart your shell or terminal."
    fi
    
    echo ""
}

print_summary() {
    log_info "Uninstallation Summary"
    echo "=================================================="
    echo ""
    
    log_success "Corplang has been removed from your system"
    echo ""
    
    log_info "Next steps:"
    echo "  1. Restart your shell or terminal"
    echo "  2. Verify removal:"
    echo "     which mf  # Should return nothing"
    echo ""
    
    local os=$(detect_os)
    if [ "$os" = "windows" ]; then
        echo "  3. On Windows, you may also want to:"
        echo "     - Remove PATH entries via System Settings > Environment Variables"
        echo ""
    fi
}

confirm_uninstall() {
    if [ "$YES" = true ]; then
        return 0
    fi
    
    echo -e "${BOLD}Corplang Uninstaller${RESET}"
    echo "=================================================="
    echo ""
    log_warn "This will remove Corplang from your system:"
    echo "  • Installation directory: $INSTALL_DIR"
    echo "  • Symlinks in /usr/local/bin (Linux/macOS)"
    echo "  • Shell configuration entries"
    echo ""
    
    read -p "Continue? [y/N]: " -r response
    echo ""
    
    case "$response" in
        [yY]|[yY][eE][sS])
            return 0
            ;;
        *)
            log_info "Uninstallation cancelled"
            exit 0
            ;;
    esac
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --yes|-y)
                YES=true
                shift
                ;;
            --force|-f)
                FORCE=true
                shift
                ;;
            --help|-h)
                echo "Corplang Uninstaller"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --yes, -y     Skip confirmation prompt"
                echo "  --force, -f   Force removal even if directory looks unexpected"
                echo "  --help, -h    Show this help message"
                echo ""
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

main() {
    parse_args "$@"
    
    confirm_uninstall
    
    remove_symlinks
    clean_shell_configs
    remove_installation_dir
    list_environment_vars
    print_summary
    
    log_success "Uninstallation complete!"
}

trap 'log_error "Uninstallation failed. Some components may need manual removal."' ERR

main "$@"
