#!/bin/bash
# ArduPilot Secure Manager - Uninstaller

INSTALL_DIR="$HOME/.local/share/ArduSecureManager"
DESKTOP_FILE="$HOME/.local/share/applications/ardupilot-secure-manager.desktop"
BIN_FILE="$HOME/.local/bin/ardupilot-secure-manager"

echo "🗑  Uninstalling ArduPilot Secure Manager..."
rm -rf "$INSTALL_DIR"
rm -f "$DESKTOP_FILE"
rm -f "$BIN_FILE"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
echo "✅ Uninstalled successfully"
