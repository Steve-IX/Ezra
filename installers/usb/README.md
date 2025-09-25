# Ezra USB/SD Card Installation

This directory contains files for creating offline installation media for Ezra.

## Creating Installation Media

### 1. Prepare USB/SD Card

- Use a USB drive or SD card with at least 2GB of free space
- Format as FAT32 or exFAT for cross-platform compatibility
- Create a directory named `ezra-offline` on the media

### 2. Download Components

Download the following files to the `ezra-offline` directory:

```
ezra-offline/
├── companion/
│   ├── package.json
│   ├── src/
│   └── node_modules/
├── agent/
│   ├── pyproject.toml
│   ├── ezra_agent/
│   └── requirements.txt
├── executor/
│   ├── pyproject.toml
│   ├── ezra_executor/
│   └── requirements.txt
├── bootstrap/
│   ├── ezra-bootstrap-linux-amd64
│   ├── ezra-bootstrap-linux-arm64
│   ├── ezra-bootstrap-windows-amd64.exe
│   └── ezra-bootstrap-darwin-amd64
├── installers/
│   ├── linux/install.sh
│   └── windows/install.ps1
└── README.md
```

### 3. Create Installation Script

Create a `install.sh` script on the root of the media:

```bash
#!/bin/bash
# Ezra Offline Installer

set -euo pipefail

EZRA_MEDIA_PATH="/media/ezra-offline"
if [ -d "/mnt/ezra-offline" ]; then
    EZRA_MEDIA_PATH="/mnt/ezra-offline"
fi

echo "Ezra Offline Installer"
echo "Media path: $EZRA_MEDIA_PATH"

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
else
    echo "Unsupported platform: $OSTYPE"
    exit 1
fi

# Run platform-specific installer
if [ "$PLATFORM" = "linux" ]; then
    chmod +x "$EZRA_MEDIA_PATH/installers/linux/install.sh"
    "$EZRA_MEDIA_PATH/installers/linux/install.sh" --offline
elif [ "$PLATFORM" = "windows" ]; then
    powershell -ExecutionPolicy Bypass -File "$EZRA_MEDIA_PATH/installers/windows/install.ps1" -Offline
fi
```

## Installation Process

### Linux

1. Insert USB/SD card
2. Mount the media (usually auto-mounted)
3. Navigate to the media directory
4. Run: `chmod +x install.sh && ./install.sh`

### Windows

1. Insert USB/SD card
2. Open PowerShell as Administrator
3. Navigate to the media directory
4. Run: `.\install.ps1 -Offline`

## Verification

After installation, verify the installation:

```bash
# Check services
systemctl status ezra-agent ezra-companion

# Check logs
journalctl -u ezra-agent -u ezra-companion

# Test connection
curl http://localhost:3000/health
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you're running as root/administrator
2. **Missing Dependencies**: Install Python 3.11+ and Node.js 18+
3. **Service Won't Start**: Check logs and configuration files
4. **Network Issues**: Verify companion server is accessible

### Log Locations

- Linux: `/var/log/ezra/`
- Windows: `C:\ProgramData\Ezra\logs\`

### Configuration Files

- Linux: `/etc/ezra/`
- Windows: `C:\ProgramData\Ezra\config\`

## Security Notes

- Offline installation media should be created from trusted sources
- Verify checksums and signatures when available
- Keep installation media secure and up-to-date
- Regularly update installed components
