# Ezra Windows Installer
# This script installs Ezra on Windows systems

param(
    [string]$CompanionUrl = "http://localhost:3000",
    [string]$DeviceId = "",
    [switch]$Offline,
    [switch]$Force,
    [switch]$Verbose,
    [switch]$Help
)

# Configuration
$EzraVersion = "0.1.0"
$EzraUser = "ezra"
$EzraHome = "C:\Program Files\Ezra"
$EzraData = "C:\ProgramData\Ezra"
$EzraConfig = "C:\ProgramData\Ezra\config"
$EzraLog = "C:\ProgramData\Ezra\logs"

# Default values
$CompanionUrl = if ($CompanionUrl) { $CompanionUrl } else { "http://localhost:3000" }
$DeviceId = if ($DeviceId) { $DeviceId } else { "ezra_$env:COMPUTERNAME" }
$OfflineMode = $Offline
$VerboseMode = $Verbose
$ForceMode = $Force

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Show-Help {
    Write-Host @"
Ezra Windows Installer

USAGE:
    .\install.ps1 [OPTIONS]

OPTIONS:
    -CompanionUrl URL    Companion server URL (default: http://localhost:3000)
    -DeviceId ID         Device identifier
    -Offline             Install in offline mode
    -Force               Force installation (overwrite existing)
    -Verbose             Enable verbose logging
    -Help                Show this help message

EXAMPLES:
    # Online installation
    .\install.ps1 -CompanionUrl https://companion.ezra.dev

    # Offline installation
    .\install.ps1 -Offline

    # Custom device ID
    .\install.ps1 -DeviceId my-device-001

For more information, visit: https://github.com/ezra/ezra
"@
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Detect system information
function Get-SystemInfo {
    Write-Info "Detecting system information..."
    
    $os = Get-WmiObject -Class Win32_OperatingSystem
    $arch = if ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "x86" }
    
    Write-Info "Detected: Windows $($os.Version) on $arch"
    
    return @{
        OS = "windows"
        Version = $os.Version
        Architecture = $arch
    }
}

# Check dependencies
function Test-Dependencies {
    Write-Info "Checking dependencies..."
    
    $missingDeps = @()
    
    # Check for PowerShell 5.1+
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        $missingDeps += "PowerShell 5.1+"
    }
    
    # Check for .NET Framework 4.8+
    try {
        $dotnetVersion = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" -Name Release
        if ($dotnetVersion.Release -lt 528040) {
            $missingDeps += ".NET Framework 4.8+"
        }
    } catch {
        $missingDeps += ".NET Framework 4.8+"
    }
    
    # Check for Python 3.11+
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -notmatch "Python 3\.(1[1-9]|[2-9][0-9])") {
            $missingDeps += "Python 3.11+"
        }
    } catch {
        $missingDeps += "Python 3.11+"
    }
    
    # Check for Node.js 18+
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -notmatch "v(1[8-9]|[2-9][0-9])") {
            $missingDeps += "Node.js 18+"
        }
    } catch {
        $missingDeps += "Node.js 18+"
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Error "Missing dependencies: $($missingDeps -join ', ')"
        Write-Info "Please install the missing dependencies and try again"
        exit 1
    }
    
    Write-Success "All dependencies satisfied"
}

# Install dependencies
function Install-Dependencies {
    Write-Info "Installing dependencies..."
    
    # Check if Chocolatey is available
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Info "Installing dependencies with Chocolatey..."
        choco install -y python nodejs
    } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "Installing dependencies with winget..."
        winget install Python.Python.3.11
        winget install OpenJS.NodeJS
    } else {
        Write-Warning "No package manager found (Chocolatey or winget)"
        Write-Info "Please install Python 3.11+ and Node.js 18+ manually"
    }
}

# Create directories
function New-Directories {
    Write-Info "Creating directories..."
    
    $dirs = @(
        $EzraHome,
        $EzraData,
        $EzraConfig,
        $EzraLog,
        "$EzraData\cache",
        "$EzraData\backups"
    )
    
    foreach ($dir in $dirs) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Created directories"
}

# Download components
function Get-Components {
    Write-Info "Downloading components..."
    
    if ($OfflineMode) {
        Write-Info "Offline mode - skipping download"
        return
    }
    
    $baseUrl = "https://github.com/ezra/ezra/releases/download/v$EzraVersion"
    $components = @("companion", "agent", "executor")
    
    foreach ($component in $components) {
        $url = "$baseUrl/ezra-$component-windows-amd64.zip"
        $file = "$env:TEMP\ezra-$component.zip"
        
        Write-Info "Downloading $component..."
        try {
            Invoke-WebRequest -Uri $url -OutFile $file
            Write-Success "Downloaded $component"
        } catch {
            Write-Error "Failed to download $component"
            exit 1
        }
    }
}

# Install components
function Install-Components {
    Write-Info "Installing components..."
    
    # Install companion server
    Install-Companion
    
    # Install agent
    Install-Agent
    
    # Install executor
    Install-Executor
    
    Write-Success "All components installed"
}

# Install companion server
function Install-Companion {
    Write-Info "Installing companion server..."
    
    $zipFile = "$env:TEMP\ezra-companion.zip"
    if (Test-Path $zipFile) {
        Expand-Archive -Path $zipFile -DestinationPath "$EzraHome\companion" -Force
    }
    
    # Install Node.js dependencies
    Set-Location "$EzraHome\companion"
    npm install --production
    
    # Create companion configuration
    $config = @{
        port = 3000
        host = "0.0.0.0"
        llm_providers = @{
            openai = @{
                api_key = ""
                models = @("gpt-4", "gpt-3.5-turbo")
            }
            anthropic = @{
                api_key = ""
                models = @("claude-3-opus", "claude-3-sonnet")
            }
            google = @{
                api_key = ""
                models = @("gemini-pro")
            }
        }
        signing = @{
            private_key = ""
            public_key = ""
        }
    } | ConvertTo-Json -Depth 10
    
    $config | Out-File -FilePath "$EzraConfig\companion.json" -Encoding UTF8
}

# Install agent
function Install-Agent {
    Write-Info "Installing agent..."
    
    $zipFile = "$env:TEMP\ezra-agent.zip"
    if (Test-Path $zipFile) {
        Expand-Archive -Path $zipFile -DestinationPath "$EzraHome\agent" -Force
    }
    
    # Install Python dependencies
    Set-Location "$EzraHome\agent"
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create agent configuration
    $config = @{
        companion_url = $CompanionUrl
        device_id = $DeviceId
        data_dir = $EzraData
        cache_dir = "$EzraData\cache"
        backup_dir = "$EzraData\backups"
        log_level = "info"
    } | ConvertTo-Json -Depth 10
    
    $config | Out-File -FilePath "$EzraConfig\agent.json" -Encoding UTF8
}

# Install executor
function Install-Executor {
    Write-Info "Installing executor..."
    
    $zipFile = "$env:TEMP\ezra-executor.zip"
    if (Test-Path $zipFile) {
        Expand-Archive -Path $zipFile -DestinationPath "$EzraHome\executor" -Force
    }
    
    # Install Python dependencies
    Set-Location "$EzraHome\executor"
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Create Windows service
function New-WindowsService {
    Write-Info "Creating Windows service..."
    
    # Create service for agent
    $agentService = @"
[Unit]
Description=Ezra Agent
After=network.target

[Service]
Type=simple
User=$EzraUser
WorkingDirectory=$EzraHome\agent
ExecStart=$EzraHome\agent\venv\Scripts\python.exe main.py start --daemon
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"@
    
    $agentService | Out-File -FilePath "$EzraConfig\ezra-agent.service" -Encoding UTF8
    
    # Create service for companion
    $companionService = @"
[Unit]
Description=Ezra Companion Server
After=network.target

[Service]
Type=simple
User=$EzraUser
WorkingDirectory=$EzraHome\companion
ExecStart=node index.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"@
    
    $companionService | Out-File -FilePath "$EzraConfig\ezra-companion.service" -Encoding UTF8
    
    Write-Success "Created Windows services"
}

# Start services
function Start-Services {
    Write-Info "Starting services..."
    
    # Start agent service
    try {
        Start-Service -Name "EzraAgent" -ErrorAction SilentlyContinue
        Write-Success "Agent service started"
    } catch {
        Write-Warning "Failed to start agent service (may need manual setup)"
    }
    
    # Start companion service
    try {
        Start-Service -Name "EzraCompanion" -ErrorAction SilentlyContinue
        Write-Success "Companion service started"
    } catch {
        Write-Warning "Failed to start companion service (may need manual setup)"
    }
}

# Cleanup
function Remove-TempFiles {
    Write-Info "Cleaning up..."
    
    # Remove temporary files
    Remove-Item "$env:TEMP\ezra-*.zip" -Force -ErrorAction SilentlyContinue
    
    Write-Success "Cleanup completed"
}

# Main installation function
function Start-Installation {
    Write-Info "Starting Ezra installation..."
    
    if ($Help) {
        Show-Help
        return
    }
    
    # Check if running as administrator
    if (!(Test-Administrator)) {
        Write-Error "This script must be run as administrator"
        exit 1
    }
    
    $systemInfo = Get-SystemInfo
    Test-Dependencies
    
    if ($ForceMode) {
        Write-Warning "Force mode enabled - existing installation will be overwritten"
    }
    
    New-Directories
    Get-Components
    Install-Components
    New-WindowsService
    Start-Services
    Remove-TempFiles
    
    Write-Success "Ezra installation completed successfully!"
    Write-Info "Services are running and enabled"
    Write-Info "Check status with: Get-Service EzraAgent, EzraCompanion"
    Write-Info "View logs in: $EzraLog"
}

# Run main function
Start-Installation
