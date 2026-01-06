#!/usr/bin/env bash
#
# Corplang Shell Integration
# Source this file in your shell config to enable Corplang features
#
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile:
#   source ~/.corplang/corplang.sh
#

# Load CORPLANG_ACTIVE_VERSION if set
if [ -f "$HOME/.corplang/version.env" ]; then
    source "$HOME/.corplang/version.env"
fi

# mf-set-version: Helper to set version and load it immediately
mf-set-version() {
    if [ -z "$1" ]; then
        echo "Usage: mf-set-version <version>"
        echo "Example: mf-set-version v1.1.3-linux"
        return 1
    fi
    
    # Call mf versions set
    local output=$(mf versions set "$1" 2>&1)
    echo "$output"
    
    # Extract version from output and load it
    if echo "$output" | grep -q "Active version set to"; then
        export CORPLANG_ACTIVE_VERSION="$1"
        echo "✓ Version loaded in current shell"
    fi
}

# mf-version: Show current active version
mf-version() {
    if [ -n "$CORPLANG_ACTIVE_VERSION" ]; then
        echo "Active version: $CORPLANG_ACTIVE_VERSION"
    else
        echo "No active version set"
    fi
}
