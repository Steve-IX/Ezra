#!/bin/bash

# Ezra Linux Installer
# This script installs Ezra on Linux systems

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EZRA_VERSION="0.1.0"
EZRA_USER="ezra"
EZRA_GROUP="ezra"
EZRA_HOME="/opt/ezra"
EZRA_DATA="/var/lib/ezra"
EZRA_CONFIG="/etc/ezra"
EZRA_LOG="/var/log/ezra"

# Default values
COMPANION_URL="http://localhost:3000"
DEVICE_ID=""
OFFLINE_MODE=false
VERBOSE=false
FORCE=false

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
Ezra Linux Installer

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -c, --companion-url URL    Companion server URL (default: http://localhost:3000)
    -d, --device-id ID         Device identifier
    -o, --offline              Install in offline mode
    -f, --force                Force installation (overwrite existing)
    -v, --verbose              Enable verbose logging
    -h, --help                 Show this help message

EXAMPLES:
    # Online installation
    $0 --companion-url https://companion.ezra.dev

    # Offline installation
    $0 --offline

    # Custom device ID
    $0 --device-id my-device-001

For more information, visit: https://github.com/ezra/ezra
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--companion-url)
            COMPANION_URL="$2"
            shift 2
            ;;
        -d|--device-id)
            DEVICE_ID="$2"
            shift 2
            ;;
        -o|--offline)
            OFFLINE_MODE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root"
    exit 1
fi

# Detect system information
detect_system() {
    log_info "Detecting system information..."
    
    # Detect distribution
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO="$ID"
        DISTRO_VERSION="$VERSION_ID"
    else
        log_error "Cannot detect Linux distribution"
        exit 1
    fi
    
    # Detect architecture
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)
            ARCH="amd64"
            ;;
        aarch64|arm64)
            ARCH="arm64"
            ;;
        armv7l)
            ARCH="arm"
            ;;
        *)
            log_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    log_info "Detected: $DISTRO $DISTRO_VERSION on $ARCH"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    # Check for required commands
    for cmd in curl wget tar gzip; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Check for Python 3.11+
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    else
        python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [[ $(echo "$python_version < 3.11" | bc -l) -eq 1 ]]; then
            missing_deps+=("python3.11+")
        fi
    fi
    
    # Check for Node.js 18+
    if ! command -v node &> /dev/null; then
        missing_deps+=("nodejs")
    else
        node_version=$(node --version | cut -d'v' -f2)
        if [[ $(echo "$node_version < 18.0.0" | bc -l) -eq 1 ]]; then
            missing_deps+=("nodejs18+")
        fi
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and try again"
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get update
            apt-get install -y curl wget tar gzip python3 python3-pip python3-venv nodejs npm
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y curl wget tar gzip python3 python3-pip nodejs npm
            else
                yum install -y curl wget tar gzip python3 python3-pip nodejs npm
            fi
            ;;
        arch)
            pacman -S --noconfirm curl wget tar gzip python python-pip nodejs npm
            ;;
        *)
            log_warning "Unknown distribution: $DISTRO"
            log_info "Please install the following dependencies manually:"
            log_info "  - curl, wget, tar, gzip"
            log_info "  - python3 (3.11+), pip"
            log_info "  - nodejs (18+), npm"
            ;;
    esac
}

# Create system user
create_user() {
    log_info "Creating system user..."
    
    if ! id "$EZRA_USER" &> /dev/null; then
        useradd -r -s /bin/false -d "$EZRA_HOME" -c "Ezra Agent" "$EZRA_USER"
        log_success "Created user: $EZRA_USER"
    else
        log_info "User $EZRA_USER already exists"
    fi
}

# Create directories
create_directories() {
    log_info "Creating directories..."
    
    local dirs=(
        "$EZRA_HOME"
        "$EZRA_DATA"
        "$EZRA_CONFIG"
        "$EZRA_LOG"
        "$EZRA_DATA/cache"
        "$EZRA_DATA/backups"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        chown "$EZRA_USER:$EZRA_GROUP" "$dir"
        chmod 755 "$dir"
    done
    
    log_success "Created directories"
}

# Download components
download_components() {
    log_info "Downloading components..."
    
    if [[ "$OFFLINE_MODE" == "true" ]]; then
        log_info "Offline mode - skipping download"
        return
    fi
    
    local base_url="https://github.com/ezra/ezra/releases/download/v$EZRA_VERSION"
    local components=("companion" "agent" "executor")
    
    for component in "${components[@]}"; do
        local url="$base_url/ezra-$component-linux-$ARCH.tar.gz"
        local file="/tmp/ezra-$component.tar.gz"
        
        log_info "Downloading $component..."
        if curl -L -o "$file" "$url"; then
            log_success "Downloaded $component"
        else
            log_error "Failed to download $component"
            exit 1
        fi
    done
}

# Install components
install_components() {
    log_info "Installing components..."
    
    # Install companion server
    install_companion
    
    # Install agent
    install_agent
    
    # Install executor
    install_executor
    
    log_success "All components installed"
}

# Install companion server
install_companion() {
    log_info "Installing companion server..."
    
    # Extract companion server
    if [[ -f "/tmp/ezra-companion.tar.gz" ]]; then
        tar -xzf "/tmp/ezra-companion.tar.gz" -C "$EZRA_HOME"
    fi
    
    # Install Node.js dependencies
    cd "$EZRA_HOME/companion"
    npm install --production
    
    # Create companion configuration
    cat > "$EZRA_CONFIG/companion.json" << EOF
{
  "port": 3000,
  "host": "0.0.0.0",
  "llm_providers": {
    "openai": {
      "api_key": "",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    },
    "anthropic": {
      "api_key": "",
      "models": ["claude-3-opus", "claude-3-sonnet"]
    },
    "google": {
      "api_key": "",
      "models": ["gemini-pro"]
    }
  },
  "signing": {
    "private_key": "",
    "public_key": ""
  }
}
EOF
    
    chown "$EZRA_USER:$EZRA_GROUP" "$EZRA_CONFIG/companion.json"
    chmod 600 "$EZRA_CONFIG/companion.json"
}

# Install agent
install_agent() {
    log_info "Installing agent..."
    
    # Extract agent
    if [[ -f "/tmp/ezra-agent.tar.gz" ]]; then
        tar -xzf "/tmp/ezra-agent.tar.gz" -C "$EZRA_HOME"
    fi
    
    # Install Python dependencies
    cd "$EZRA_HOME/agent"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create agent configuration
    cat > "$EZRA_CONFIG/agent.json" << EOF
{
  "companion_url": "$COMPANION_URL",
  "device_id": "$DEVICE_ID",
  "data_dir": "$EZRA_DATA",
  "cache_dir": "$EZRA_DATA/cache",
  "backup_dir": "$EZRA_DATA/backups",
  "log_level": "info"
}
EOF
    
    chown "$EZRA_USER:$EZRA_GROUP" "$EZRA_CONFIG/agent.json"
    chmod 600 "$EZRA_CONFIG/agent.json"
}

# Install executor
install_executor() {
    log_info "Installing executor..."
    
    # Extract executor
    if [[ -f "/tmp/ezra-executor.tar.gz" ]]; then
        tar -xzf "/tmp/ezra-executor.tar.gz" -C "$EZRA_HOME"
    fi
    
    # Install Python dependencies
    cd "$EZRA_HOME/executor"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Create systemd service
create_systemd_service() {
    log_info "Creating systemd service..."
    
    cat > "/etc/systemd/system/ezra-agent.service" << EOF
[Unit]
Description=Ezra Agent
After=network.target

[Service]
Type=simple
User=$EZRA_USER
Group=$EZRA_GROUP
WorkingDirectory=$EZRA_HOME/agent
ExecStart=$EZRA_HOME/agent/venv/bin/python main.py start --daemon
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    cat > "/etc/systemd/system/ezra-companion.service" << EOF
[Unit]
Description=Ezra Companion Server
After=network.target

[Service]
Type=simple
User=$EZRA_USER
Group=$EZRA_GROUP
WorkingDirectory=$EZRA_HOME/companion
ExecStart=/usr/bin/node index.js
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    log_success "Created systemd services"
}

# Start services
start_services() {
    log_info "Starting services..."
    
    # Enable services
    systemctl enable ezra-agent
    systemctl enable ezra-companion
    
    # Start services
    systemctl start ezra-agent
    systemctl start ezra-companion
    
    # Check status
    if systemctl is-active --quiet ezra-agent; then
        log_success "Agent service started"
    else
        log_error "Failed to start agent service"
        exit 1
    fi
    
    if systemctl is-active --quiet ezra-companion; then
        log_success "Companion service started"
    else
        log_error "Failed to start companion service"
        exit 1
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up..."
    
    # Remove temporary files
    rm -f /tmp/ezra-*.tar.gz
    
    log_success "Cleanup completed"
}

# Main installation function
main() {
    log_info "Starting Ezra installation..."
    
    detect_system
    check_dependencies
    
    if [[ "$FORCE" == "true" ]]; then
        log_warning "Force mode enabled - existing installation will be overwritten"
    fi
    
    create_user
    create_directories
    download_components
    install_components
    create_systemd_service
    start_services
    cleanup
    
    log_success "Ezra installation completed successfully!"
    log_info "Services are running and enabled"
    log_info "Check status with: systemctl status ezra-agent ezra-companion"
    log_info "View logs with: journalctl -u ezra-agent -u ezra-companion"
}

# Run main function
main "$@"
