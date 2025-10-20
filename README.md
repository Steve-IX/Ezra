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

## 📦 Monorepo Structure

This is a **pnpm workspace** monorepo containing multiple interconnected packages:

### `companion/` - Companion Server
- **TypeScript + Fastify** server with OpenAPI docs
- **Multi-provider LLM routing** with fallback and rate limiting
- **Ed25519 signing** for action plans
- **Zod validation** for all requests/responses
- **Dependencies**: `@ezra/schemas`, Fastify, OpenAI SDK, Anthropic SDK, Google Generative AI

### `agent/` - Device Agent
- **Python 3.11+** daemon with systemd service
- **Device scanning** and capability detection
- **Action plan execution** with backup/rollback
- **Rich CLI** with `ezractl` command
- **Dependencies**: Typer, Requests, Pydantic, Cryptography

### `executor/` - Executor Library
- **Python library** with system adapters
- **Platform adapters** for Linux, Windows, Android
- **Package management** (apt, yum, choco, winget, etc.)
- **File operations** with permission handling
- **Dependencies**: Pydantic, psutil

### `schemas/` - Shared Types
- **TypeScript type definitions** generated from JSON schemas
- **Zod/TypeBox schemas** for validation
- **Python stubs** via `datamodel-codegen` (planned)
- **Shared across** companion and agent

### `bootstrap/` - Bootstrap Installer
- **Go static binary** for installation
- **Online/offline** installation modes
- **Cross-platform** detection and setup (linux/amd64, linux/arm64, windows/amd64)
- **System service** configuration

### `installers/` - Platform Installers
- **Linux**: Bash installation script
- **Windows**: PowerShell installation script
- **USB/SD**: Offline installation manifests

### `docs/` - Documentation
- Project documentation (planned: MkDocs)
- Architecture diagrams
- API references

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

# Configure companion server
cd companion
cp .env.example .env
# Edit .env and add your API keys (see Configuration section)

# Configure agent
cd ../agent
cp .env.example .env
# Edit .env with companion URL and keys

# Build all components
cd ..
pnpm build

# Start companion server
cd companion
pnpm start

# Start agent (in another terminal)
cd agent
python -m ezra_agent.main start
```

## 🔧 Configuration

### Quick Setup (Recommended)

Ezra provides **interactive setup wizards** that guide you through configuration:

#### Companion Server Setup

```bash
cd companion
pnpm install
pnpm setup
```

The wizard will:
- Prompt for your API keys (with validation)
- Configure provider preferences
- Set up signing key paths
- Create a secure `.env` file with proper permissions

#### Device Agent Setup

```bash
cd agent
pip install -e .
ezractl setup
```

The wizard will:
- Prompt for companion server URL (with connection test)
- Configure policy verification paths
- Set up device directories
- Create a secure `.env` file with proper permissions

### Manual Configuration

If you prefer to configure manually, Ezra uses environment variables for sensitive configuration. **Never commit `.env` files to version control** - they are already in `.gitignore`.

#### Companion Server Configuration

1. Copy the environment template:
```bash
cd companion
cp .env.example .env
```

2. Edit `.env` and add your actual API keys:
   - **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Anthropic API Key**: Get from [Anthropic Console](https://console.anthropic.com/settings/keys)
   - **Google API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. Generate Ed25519 signing keys:
```bash
# Generate private key
openssl genpkey -algorithm ed25519 -out policy_priv.key

# Extract public key
openssl pkey -in policy_priv.key -pubout -out policy_pub.key

# Update PLAN_SIGNING_PRIVATE_KEY_PATH in .env
```

4. (Optional) For advanced configuration, you can also use `config.json`. See `config.example.json` for the structure.

#### Device Agent Configuration

1. Copy the environment template:
```bash
cd agent
cp .env.example .env
```

2. Edit `.env` and configure:
   - **COMPANION_BASE_URL**: URL of your companion server (e.g., `https://companion.example.com:8443`)
   - **POLICY_PUB_KEY_PATH**: Path to the Ed25519 public key (must match companion's private key)
   - **DEVICE_ENROLLMENT_TOKEN**: (Optional) Token for device enrollment

### Configuration Files vs Environment Variables

- **`.env` files** (gitignored): Store sensitive data like API keys and secrets
- **`.env.example` files** (committed): Templates showing what variables are needed
- **`config.json` files**: Can be used for non-sensitive configuration alongside `.env`

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
- **Environment variables**: Sensitive data stored in `.env` files (never committed to git)
- **API key protection**: All API keys should be kept secure and rotated regularly

## 🛠️ Development

### Prerequisites

- **Node.js** 18+ and **pnpm** 8+
- **Python** 3.11+
- **Go** 1.21+
- **OpenSSL** (for generating Ed25519 keys)

### Setup

```bash
# Install dependencies
pnpm install

# Install Python dependencies with dev tools
cd agent && pip install -e .[dev]
cd ../executor && pip install -e .[dev]

# Install Go dependencies
cd ../bootstrap && go mod download

# Set up environment configuration
cd ../companion
cp .env.example .env
# Edit .env and add your API keys

cd ../agent
cp .env.example .env
# Edit .env with companion URL

# Generate signing keys for development
openssl genpkey -algorithm ed25519 -out ../companion/policy_priv.key
openssl pkey -in ../companion/policy_priv.key -pubout -out ../agent/policy_pub.key
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
