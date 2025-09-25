# Ezra - Universal System Agent

[![CI](https://github.com/ezra/ezra/actions/workflows/ci.yml/badge.svg)](https://github.com/ezra/ezra/actions/workflows/ci.yml)
[![Security](https://github.com/ezra/ezra/actions/workflows/security.yml/badge.svg)](https://github.com/ezra/ezra/actions/workflows/security.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Ezra is a universal, Jarvis-style system agent that runs as a **thin device agent** and a **companion server**. The device agent scans hardware/OS/firmware, requests a **signed JSON action plan** from the companion (which calls LLMs), verifies the signature, shows a human-readable diff, requires consent, then executes with backups/rollback.

## 🚀 Features

- **Multi-provider LLM support**: OpenAI, Anthropic, Google (Gemini) with **AUTO** mode selection
- **Signed action plans**: Cryptographically signed JSON plans with Ed25519
- **Cross-platform**: Linux, Windows, Android, and console devices
- **Offline installation**: USB/SD card installation support
- **High-risk operations**: Jailbreak, DRM bypass, unsigned boot mods with explicit consent
- **Backup & rollback**: Automatic backups before high-risk operations
- **System adapters**: Platform-specific adapters for different operating systems

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Device Agent  │◄──►│ Companion Server│◄──►│   LLM Providers  │
│   (Python)      │    │   (TypeScript)   │    │ OpenAI/Anthropic│
│                 │    │                 │    │ Google/Others   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│    Executor     │    │   Action Plans   │
│   (Python)      │    │   (Signed JSON)  │
│                 │    │                 │
└─────────────────┘    └─────────────────┘
```

## 📦 Components

### Companion Server (`companion/`)
- **TypeScript + Fastify** server with OpenAPI docs
- **Multi-provider LLM routing** with fallback and rate limiting
- **Ed25519 signing** for action plans
- **Zod validation** for all requests/responses

### Device Agent (`agent/`)
- **Python 3.11** daemon with systemd service
- **Device scanning** and capability detection
- **Action plan execution** with backup/rollback
- **Rich CLI** with `ezractl` command

### Executor Library (`executor/`)
- **Python library** with system adapters
- **Platform adapters** for Linux, Windows, Android
- **Package management** (apt, yum, choco, winget, etc.)
- **File operations** with permission handling

### Bootstrap Installer (`bootstrap/`)
- **Go static binary** for installation
- **Online/offline** installation modes
- **Cross-platform** detection and setup
- **System service** configuration

## 🚀 Quick Start

### Online Installation

```bash
# Linux
curl -fsSL https://install.ezra.dev | bash

# Windows (PowerShell)
iwr -useb https://install.ezra.dev | iex
```

### Offline Installation

1. Download the offline installer from [Releases](https://github.com/ezra/ezra/releases)
2. Extract to USB/SD card
3. Run the installation script

```bash
# Linux
./install.sh --offline

# Windows
.\install.ps1 -Offline
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/ezra/ezra.git
cd ezra

# Install dependencies
pnpm install

# Build components
pnpm build

# Start companion server
cd companion
pnpm start

# Start agent (in another terminal)
cd agent
python -m ezra_agent.main start
```

## 🔧 Configuration

### Companion Server

Create `config.json`:

```json
{
  "port": 3000,
  "host": "0.0.0.0",
  "llm_providers": {
    "openai": {
      "api_key": "your-openai-key",
      "models": ["gpt-4", "gpt-3.5-turbo"]
    },
    "anthropic": {
      "api_key": "your-anthropic-key",
      "models": ["claude-3-opus", "claude-3-sonnet"]
    },
    "google": {
      "api_key": "your-google-key",
      "models": ["gemini-pro"]
    }
  },
  "signing": {
    "private_key": "your-ed25519-private-key",
    "public_key": "your-ed25519-public-key"
  }
}
```

### Device Agent

Create `agent-config.json`:

```json
{
  "companion_url": "http://localhost:3000",
  "device_id": "ezra_device_001",
  "data_dir": "/var/lib/ezra",
  "cache_dir": "/var/lib/ezra/cache",
  "backup_dir": "/var/lib/ezra/backups",
  "log_level": "info"
}
```

## 🎯 Usage

### Basic Commands

```bash
# Check agent status
ezractl status

# Process a request
ezractl request "Install Docker and set up a development environment"

# Scan device capabilities
ezractl scan

# Test companion connection
ezractl test
```

### High-Risk Operations

```bash
# Jailbreak device (requires explicit consent)
ezractl request "Jailbreak this device and install Cydia"

# Bypass DRM (requires explicit consent)
ezractl request "Bypass DRM protection on this media file"

# Unsigned boot modification (requires explicit consent)
ezractl request "Install custom bootloader for dual-boot"
```

## 🔒 Security

- **Cryptographic signing**: All action plans are signed with Ed25519
- **Consent required**: High-risk operations require explicit user approval
- **Backup & rollback**: Automatic backups before risky operations
- **Signature verification**: All plans are verified before execution
- **Rate limiting**: LLM API calls are rate-limited and monitored

## 🛠️ Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- Go 1.21+
- pnpm 8+

### Setup

```bash
# Install dependencies
pnpm install

# Install Python dependencies
cd agent && pip install -e .
cd ../executor && pip install -e .

# Install Go dependencies
cd bootstrap && go mod download
```

### Testing

```bash
# Run all tests
pnpm test

# Run specific component tests
cd companion && pnpm test
cd agent && python -m pytest
cd executor && python -m pytest
cd bootstrap && go test ./...
```

### Building

```bash
# Build all components
pnpm build

# Build specific components
cd companion && pnpm build
cd agent && python -m build
cd executor && python -m build
cd bootstrap && make build-all
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [Security Guide](docs/security.md)
- [Developer Guide](docs/development.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

Ezra is a powerful system agent that can perform high-risk operations including jailbreaking, DRM bypass, and system modifications. Use at your own risk. Always ensure you have proper backups and understand the implications of the operations you're requesting.

## 🆘 Support

- [GitHub Issues](https://github.com/ezra/ezra/issues)
- [Discussions](https://github.com/ezra/ezra/discussions)
- [Documentation](https://docs.ezra.dev)

---

**Ezra** - Your universal system agent. 🚀
