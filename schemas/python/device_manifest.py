"""Device Manifest Pydantic Models"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Platform(str, Enum):
    """Operating system platforms"""

    LINUX = "linux"
    WINDOWS = "windows"
    ANDROID = "android"
    CONSOLE = "console"
    UNKNOWN = "unknown"


class SELinuxStatus(str, Enum):
    """SELinux status values"""

    ENFORCING = "enforcing"
    PERMISSIVE = "permissive"
    DISABLED = "disabled"
    NOT_PRESENT = "not_present"


class StorageDeviceType(str, Enum):
    """Storage device types"""

    HDD = "hdd"
    SSD = "ssd"
    NVME = "nvme"
    EMMC = "emmc"
    SD = "sd"
    USB = "usb"
    UNKNOWN = "unknown"


class PackageManager(str, Enum):
    """Package manager types"""

    APT = "apt"
    YUM = "yum"
    DNF = "dnf"
    PACMAN = "pacman"
    ZYPPER = "zypper"
    APK = "apk"
    CHOCO = "choco"
    WINGET = "winget"
    PIP = "pip"
    NPM = "npm"
    CARGO = "cargo"
    UNKNOWN = "unknown"


class CPU(BaseModel):
    """CPU information"""

    model: str
    vendor: Optional[str] = None
    cores: int = Field(..., gt=0)
    threads: Optional[int] = Field(None, gt=0)
    frequency_mhz: Optional[int] = Field(None, ge=0)
    architecture: str


class GPU(BaseModel):
    """GPU information"""

    model: str
    vendor: Optional[str] = None
    vram_mb: Optional[int] = Field(None, ge=0)
    driver_version: Optional[str] = None


class Memory(BaseModel):
    """Memory information"""

    total_bytes: int = Field(..., ge=0)
    available_bytes: Optional[int] = Field(None, ge=0)
    swap_total_bytes: Optional[int] = Field(None, ge=0)
    swap_used_bytes: Optional[int] = Field(None, ge=0)


class Hardware(BaseModel):
    """Hardware information"""

    cpu: CPU
    gpu: Optional[GPU] = None
    memory: Memory
    chipset: Optional[str] = None


class StorageDevice(BaseModel):
    """Storage device information"""

    device: str
    model: Optional[str] = None
    type: Optional[StorageDeviceType] = None
    size_bytes: int = Field(..., ge=0)


class Partition(BaseModel):
    """Partition information"""

    device: str
    mount_point: str
    fstype: str
    size_bytes: int = Field(..., ge=0)
    used_bytes: Optional[int] = Field(None, ge=0)
    uuid: Optional[str] = None
    label: Optional[str] = None


class Storage(BaseModel):
    """Storage information"""

    devices: list[StorageDevice]
    partitions: Optional[list[Partition]] = None


class Boot(BaseModel):
    """Boot configuration information"""

    secure_boot_enabled: Optional[bool] = None
    boot_loader: Optional[str] = None
    boot_loader_version: Optional[str] = None
    boot_hash: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$")
    uefi_mode: Optional[bool] = None
    tpm_present: Optional[bool] = None
    tpm_version: Optional[str] = None


class BIOS(BaseModel):
    """BIOS/UEFI information"""

    vendor: Optional[str] = None
    version: Optional[str] = None
    release_date: Optional[str] = None


class Firmware(BaseModel):
    """Firmware information"""

    bios: Optional[BIOS] = None
    ec_version: Optional[str] = None
    me_version: Optional[str] = None


class OS(BaseModel):
    """Operating system information"""

    platform: Platform
    distribution: str
    version: Optional[str] = None
    kernel: str
    architecture: str
    init_system: Optional[str] = None
    selinux_status: Optional[SELinuxStatus] = None
    apparmor_enabled: Optional[bool] = None


class Package(BaseModel):
    """Installed package information"""

    name: str
    version: str
    manager: PackageManager
    architecture: Optional[str] = None


class FileInfo(BaseModel):
    """File information with integrity hash"""

    path: str
    sha256: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    size_bytes: Optional[int] = Field(None, ge=0)
    permissions: Optional[str] = None
    owner: Optional[str] = None


class Logs(BaseModel):
    """System log tails"""

    dmesg: Optional[list[str]] = None
    syslog: Optional[list[str]] = None
    journal: Optional[list[str]] = None


class DeviceManifest(BaseModel):
    """Complete device manifest"""

    manifest_id: UUID
    device_id: str
    captured_at: datetime
    hardware: Hardware
    storage: Storage
    boot: Optional[Boot] = None
    firmware: Optional[Firmware] = None
    os: OS
    packages: Optional[list[Package]] = None
    files: Optional[list[FileInfo]] = None
    logs: Optional[Logs] = None
    capabilities: Optional[list[str]] = None
    manifest_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "manifest_id": "550e8400-e29b-41d4-a716-446655440000",
                "device_id": "device-001",
                "captured_at": "2025-10-20T12:00:00Z",
                "hardware": {
                    "cpu": {
                        "model": "Intel Core i7-9700K",
                        "cores": 8,
                        "architecture": "x86_64",
                    },
                    "memory": {"total_bytes": 16777216000},
                },
                "storage": {
                    "devices": [
                        {
                            "device": "/dev/sda",
                            "type": "ssd",
                            "size_bytes": 512000000000,
                        },
                    ],
                },
                "os": {
                    "platform": "linux",
                    "distribution": "Ubuntu",
                    "kernel": "5.15.0-76-generic",
                    "architecture": "x86_64",
                },
                "manifest_hash": "a" * 64,
            },
        }

