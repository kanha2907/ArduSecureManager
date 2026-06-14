#!/bin/bash
# ============================================================
#  ArduPilot Secure Manager - Installer
#  Supports: Ubuntu 20.04+, Debian 11+, Fedora 36+, Arch
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

APPNAME="ArduPilot Secure Manager"
INSTALL_DIR="$HOME/.local/share/ArduSecureManager"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_DIR="$HOME/.local/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔐  ArduPilot Secure Manager  - Installer     ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

print_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif command -v lsb_release &>/dev/null; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

install_system_deps() {
    local distro=$(detect_distro)
    print_step "Installing system dependencies for: $distro"

    case "$distro" in
        ubuntu|debian|linuxmint|pop)
            sudo apt-get update -qq
            sudo apt-get install -y \
                python3 python3-pip python3-tk python3-serial \
                git build-essential curl wget \
                gcc-arm-none-eabi 2>/dev/null || true
            ;;
        fedora|rhel|centos)
            sudo dnf install -y \
                python3 python3-pip python3-tkinter \
                git gcc-arm-none-eabi-gcc 2>/dev/null || true
            ;;
        arch|manjaro|endeavouros)
            sudo pacman -Sy --noconfirm \
                python python-pip tk python-pyserial \
                git arm-none-eabi-gcc 2>/dev/null || true
            ;;
        *)
            print_warn "Unknown distro. Trying generic install..."
            python3 -m ensurepip --upgrade 2>/dev/null || true
            ;;
    esac
    print_ok "System dependencies installed"
}

install_python_deps() {
    print_step "Installing Python dependencies..."
    pip3 install --break-system-packages -q \
        pyserial \
        "pymonocypher==3.1.3.2" \
        pymavlink \
        MAVProxy 2>/dev/null || \
    pip3 install -q \
        pyserial \
        "pymonocypher==3.1.3.2" \
        pymavlink 2>/dev/null || true
    print_ok "Python dependencies installed"
}

install_app() {
    print_step "Installing application..."
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$BIN_DIR"

    # Copy main app
    cp "$SCRIPT_DIR/ardupilot_secure_manager.py" "$INSTALL_DIR/"

    # Create launcher script
    cat > "$BIN_DIR/ardupilot-secure-manager" << LAUNCHER
#!/bin/bash
python3 "$INSTALL_DIR/ardupilot_secure_manager.py" "\$@"
LAUNCHER
    chmod +x "$BIN_DIR/ardupilot-secure-manager"

    # Create desktop entry
    cat > "$DESKTOP_DIR/ardupilot-secure-manager.desktop" << DESKTOP
[Desktop Entry]
Name=ArduPilot Secure Manager
GenericName=Firmware Manager
Comment=Secure firmware build, sign and flash tool for ArduPilot
Exec=$BIN_DIR/ardupilot-secure-manager
Icon=$INSTALL_DIR/icon.svg
Type=Application
Categories=Utility;Development;Science;
Terminal=false
StartupNotify=true
Keywords=ardupilot;drone;firmware;security;flash;
DESKTOP

    # Create icon
    cat > "$INSTALL_DIR/icon.svg" << 'ICON'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="40" fill="#0d0f14"/>
  <rect x="8" y="8" width="240" height="240" rx="36" fill="none" stroke="#00d4ff" stroke-width="3" opacity="0.4"/>
  <circle cx="128" cy="95" r="35" fill="none" stroke="#00d4ff" stroke-width="8"/>
  <rect x="88" y="110" width="80" height="65" rx="10" fill="#00d4ff" opacity="0.9"/>
  <rect x="112" y="127" width="32" height="22" rx="6" fill="#0d0f14"/>
  <circle cx="128" cy="138" r="6" fill="#00d4ff"/>
  <line x1="128" y1="144" x2="128" y2="151" stroke="#00d4ff" stroke-width="3" stroke-linecap="round"/>
  <text x="128" y="210" font-size="18" text-anchor="middle" fill="#00d4ff"
        font-family="monospace" font-weight="bold" letter-spacing="2">SECURE</text>
</svg>
ICON

    # Update desktop database
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

    print_ok "Application installed to $INSTALL_DIR"
    print_ok "Launcher: $BIN_DIR/ardupilot-secure-manager"
    print_ok "Desktop entry created"
}

setup_udev_rules() {
    print_step "Setting up USB device rules (for flight controllers)..."
    RULES_FILE="/etc/udev/rules.d/99-ardupilot-fc.rules"

    sudo tee "$RULES_FILE" > /dev/null << 'UDEV'
# ArduPilot Flight Controllers - USB serial access
# CUAVv5 / Pixhawk family
SUBSYSTEM=="tty", ATTRS{idVendor}=="1209", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="26ac", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="3162", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="2dae", MODE="0666", GROUP="dialout"
# Generic USB serial
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", MODE="0666", GROUP="dialout"
UDEV

    sudo udevadm control --reload-rules 2>/dev/null || true
    sudo udevadm trigger 2>/dev/null || true

    # Add user to dialout group
    sudo usermod -aG dialout "$USER" 2>/dev/null || true
    print_ok "USB rules installed (re-login may be required)"
}

check_arm_toolchain() {
    print_step "Checking ARM toolchain..."
    if command -v arm-none-eabi-gcc &>/dev/null; then
        VER=$(arm-none-eabi-gcc --version | head -1)
        print_ok "ARM toolchain found: $VER"
    else
        print_warn "ARM toolchain not found!"
        echo "  Install with:"
        echo "  Ubuntu/Debian: sudo apt install gcc-arm-none-eabi"
        echo "  Or download from: https://developer.arm.com/downloads/-/gnu-rm"
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           Installation Complete! 🎉              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}Launch from terminal:${NC}"
    echo -e "    ${CYAN}ardupilot-secure-manager${NC}"
    echo ""
    echo -e "  ${BOLD}Or find in your app menu:${NC}"
    echo -e "    ${CYAN}ArduPilot Secure Manager${NC}"
    echo ""
    echo -e "  ${YELLOW}⚠  If USB port access fails, run:${NC}"
    echo -e "    ${CYAN}sudo usermod -aG dialout \$USER && newgrp dialout${NC}"
    echo ""
}

# ── Main ──────────────────────────────────────────────────
print_header

# Check if app file exists
if [ ! -f "$SCRIPT_DIR/ardupilot_secure_manager.py" ]; then
    print_error "ardupilot_secure_manager.py not found in $SCRIPT_DIR"
    echo "Make sure install.sh is in the same folder as ardupilot_secure_manager.py"
    exit 1
fi

install_system_deps
install_python_deps
install_app
setup_udev_rules
check_arm_toolchain
print_summary
