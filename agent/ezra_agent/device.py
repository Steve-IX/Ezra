"""Device information collection and management."""

import platform
from datetime import datetime
from typing import Any

import psutil
from pydantic import BaseModel, Field


class HardwareInfo(BaseModel):
    """Hardware information model."""

    cpu: str = Field(..., description="CPU information")
    memory: int = Field(..., description="Total memory in bytes")
    storage: int = Field(..., description="Total storage in bytes")
    gpu: str | None = Field(None, description="GPU information")


class DeviceInfo(BaseModel):
    """Device information model."""

    id: str = Field(..., description="Unique device identifier")
    platform: str = Field(..., description="Platform type")
    architecture: str = Field(..., description="System architecture")
    os: str = Field(..., description="Operating system")
    version: str = Field(..., description="OS version")
    hardware: HardwareInfo = Field(..., description="Hardware information")
    capabilities: list[str] = Field(default_factory=list, description="Device capabilities")
    timestamp: str = Field(..., description="Information collection timestamp")


class DeviceScanner:
    """Scans and collects device information."""

    def __init__(self):
        """Initialize device scanner."""
        self._capabilities: list[str] = []

    def scan(self, device_id: str) -> DeviceInfo:
        """Scan device and return information."""
        # Detect platform
        platform_name = self._detect_platform()

        # Get system information
        arch = platform.machine()
        os_name = platform.system()
        os_version = platform.release()

        # Get hardware information
        hardware = self._get_hardware_info()

        # Detect capabilities
        capabilities = self._detect_capabilities()

        return DeviceInfo(
            id=device_id,
            platform=platform_name,
            architecture=arch,
            os=os_name,
            version=os_version,
            hardware=hardware,
            capabilities=capabilities,
            timestamp=datetime.utcnow().isoformat(),
        )

    def _detect_platform(self) -> str:
        """Detect the platform type."""
        system = platform.system().lower()

        if system == "linux":
            return "linux"
        if system == "windows":
            return "windows"
        if system == "darwin":
            return "macos"  # Treat macOS as a variant of Unix
        if "android" in platform.platform().lower():
            return "android"
        return "console"  # Fallback for other systems

    def _get_hardware_info(self) -> HardwareInfo:
        """Get hardware information."""
        # CPU information
        cpu_info = platform.processor()
        if not cpu_info or cpu_info == "unknown":
            cpu_info = platform.machine()

        # Memory information
        memory = psutil.virtual_memory()
        total_memory = memory.total

        # Storage information
        storage = psutil.disk_usage("/")
        if platform.system() == "Windows":
            storage = psutil.disk_usage("C:\\")
        total_storage = storage.total

        # GPU information (basic detection)
        gpu_info = self._detect_gpu()

        return HardwareInfo(
            cpu=cpu_info,
            memory=total_memory,
            storage=total_storage,
            gpu=gpu_info,
        )

    def _detect_gpu(self) -> str | None:
        """Detect GPU information."""
        try:
            # Try to detect NVIDIA GPU
            import subprocess
            result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                  check=False, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Try to detect AMD GPU
        try:
            result = subprocess.run(["lspci"], check=False, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "vga" in line.lower() and ("amd" in line.lower() or "radeon" in line.lower()):
                        return line.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _detect_capabilities(self) -> list[str]:
        """Detect device capabilities."""
        capabilities = []

        # Basic capabilities
        capabilities.extend(["file_system", "network", "process_management"])

        # Platform-specific capabilities
        system = platform.system().lower()
        if system == "linux":
            capabilities.extend([
                "package_management",
                "systemd",
                "shell_access",
                "root_access",
            ])

            # Check for specific tools
            if self._has_command("apt"):
                capabilities.append("apt_package_manager")
            if self._has_command("yum"):
                capabilities.append("yum_package_manager")
            if self._has_command("dnf"):
                capabilities.append("dnf_package_manager")
            if self._has_command("pacman"):
                capabilities.append("pacman_package_manager")

        elif system == "windows":
            capabilities.extend([
                "powershell",
                "registry_access",
                "windows_services",
            ])

            # Check for specific tools
            if self._has_command("choco"):
                capabilities.append("chocolatey_package_manager")
            if self._has_command("winget"):
                capabilities.append("winget_package_manager")

        # Check for development tools
        if self._has_command("git"):
            capabilities.append("git")
        if self._has_command("docker"):
            capabilities.append("docker")
        if self._has_command("python"):
            capabilities.append("python")
        if self._has_command("node"):
            capabilities.append("nodejs")

        # Check for virtualization
        if self._has_command("kvm"):
            capabilities.append("kvm_virtualization")
        if self._has_command("virtualbox"):
            capabilities.append("virtualbox")

        return capabilities

    def _has_command(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            import subprocess
            result = subprocess.run(["which", command], check=False, capture_output=True, timeout=2)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_system_status(self) -> dict[str, Any]:
        """Get current system status."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent if platform.system() != "Windows" else psutil.disk_usage("C:\\").percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime": datetime.now() - datetime.fromtimestamp(psutil.boot_time()),
        }
