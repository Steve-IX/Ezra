"""Tests for Device Manifest schema"""

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from device_manifest import (
    CPU,
    BIOS,
    GPU,
    OS,
    Boot,
    DeviceManifest,
    Firmware,
    Hardware,
    Memory,
    Package,
    PackageManager,
    Partition,
    Platform,
    SELinuxStatus,
    Storage,
    StorageDevice,
    StorageDeviceType,
)


def test_cpu_creation():
    """Test creating a CPU object"""
    cpu = CPU(
        model="Intel Core i7-9700K",
        vendor="Intel",
        cores=8,
        threads=8,
        frequency_mhz=3600,
        architecture="x86_64",
    )
    assert cpu.cores == 8
    assert cpu.architecture == "x86_64"


def test_memory_creation():
    """Test creating a Memory object"""
    memory = Memory(
        total_bytes=16777216000,
        available_bytes=8388608000,
    )
    assert memory.total_bytes > 0


def test_hardware_creation():
    """Test creating complete hardware object"""
    hardware = Hardware(
        cpu=CPU(model="Intel i7", cores=8, architecture="x86_64"),
        gpu=GPU(model="NVIDIA GTX 1080", vram_mb=8192),
        memory=Memory(total_bytes=16777216000),
        chipset="Intel Z390",
    )
    assert hardware.cpu.cores == 8
    assert hardware.gpu.vram_mb == 8192


def test_storage_device():
    """Test storage device creation"""
    device = StorageDevice(
        device="/dev/sda",
        model="Samsung 970 EVO",
        type=StorageDeviceType.NVME,
        size_bytes=512000000000,
    )
    assert device.type == StorageDeviceType.NVME


def test_partition():
    """Test partition creation"""
    partition = Partition(
        device="/dev/sda1",
        mount_point="/",
        fstype="ext4",
        size_bytes=100000000000,
        used_bytes=50000000000,
        uuid="12345-67890",
    )
    assert partition.fstype == "ext4"


def test_os_creation():
    """Test OS creation"""
    os = OS(
        platform=Platform.LINUX,
        distribution="Ubuntu",
        version="22.04",
        kernel="5.15.0-76-generic",
        architecture="x86_64",
        init_system="systemd",
        selinux_status=SELinuxStatus.NOT_PRESENT,
    )
    assert os.platform == Platform.LINUX
    assert os.kernel.startswith("5.")


def test_package():
    """Test package creation"""
    pkg = Package(
        name="docker",
        version="24.0.5",
        manager=PackageManager.APT,
        architecture="amd64",
    )
    assert pkg.manager == PackageManager.APT


def test_device_manifest_creation():
    """Test creating a complete device manifest"""
    manifest = DeviceManifest(
        manifest_id=uuid4(),
        device_id="device-001",
        captured_at=datetime.now(timezone.utc),
        hardware=Hardware(
            cpu=CPU(model="Intel i7", cores=8, architecture="x86_64"),
            memory=Memory(total_bytes=16777216000),
        ),
        storage=Storage(
            devices=[
                StorageDevice(
                    device="/dev/sda",
                    type=StorageDeviceType.SSD,
                    size_bytes=512000000000,
                ),
            ],
            partitions=[
                Partition(
                    device="/dev/sda1",
                    mount_point="/",
                    fstype="ext4",
                    size_bytes=500000000000,
                ),
            ],
        ),
        os=OS(
            platform=Platform.LINUX,
            distribution="Ubuntu",
            kernel="5.15.0",
            architecture="x86_64",
        ),
        manifest_hash="a" * 64,
    )
    assert manifest.device_id == "device-001"
    assert len(manifest.storage.devices) == 1


def test_device_manifest_with_packages():
    """Test device manifest with packages"""
    manifest = DeviceManifest(
        manifest_id=uuid4(),
        device_id="device-001",
        captured_at=datetime.now(timezone.utc),
        hardware=Hardware(
            cpu=CPU(model="Intel i7", cores=8, architecture="x86_64"),
            memory=Memory(total_bytes=16777216000),
        ),
        storage=Storage(devices=[]),
        os=OS(
            platform=Platform.LINUX,
            distribution="Ubuntu",
            kernel="5.15.0",
            architecture="x86_64",
        ),
        packages=[
            Package(name="docker", version="24.0", manager=PackageManager.APT),
            Package(name="nginx", version="1.18", manager=PackageManager.APT),
        ],
        manifest_hash="b" * 64,
    )
    assert len(manifest.packages) == 2


def test_boot_configuration():
    """Test boot configuration"""
    boot = Boot(
        secure_boot_enabled=True,
        boot_loader="GRUB",
        boot_loader_version="2.06",
        uefi_mode=True,
        tpm_present=True,
        tpm_version="2.0",
    )
    assert boot.secure_boot_enabled is True
    assert boot.tpm_present is True


def test_firmware_info():
    """Test firmware information"""
    firmware = Firmware(
        bios=BIOS(vendor="AMI", version="1.2.3", release_date="2023-01-15"),
        ec_version="1.0",
    )
    assert firmware.bios.vendor == "AMI"


def test_device_manifest_json_serialization():
    """Test JSON serialization and deserialization"""
    manifest = DeviceManifest(
        manifest_id=uuid4(),
        device_id="device-001",
        captured_at=datetime.now(timezone.utc),
        hardware=Hardware(
            cpu=CPU(model="Intel i7", cores=8, architecture="x86_64"),
            memory=Memory(total_bytes=16777216000),
        ),
        storage=Storage(devices=[]),
        os=OS(
            platform=Platform.LINUX,
            distribution="Ubuntu",
            kernel="5.15.0",
            architecture="x86_64",
        ),
        manifest_hash="c" * 64,
    )

    # Serialize
    json_str = manifest.model_dump_json()
    data = json.loads(json_str)

    # Deserialize
    manifest2 = DeviceManifest.model_validate(data)
    assert manifest2.device_id == manifest.device_id
    assert manifest2.hardware.cpu.cores == 8


def test_invalid_manifest_hash():
    """Test invalid manifest hash validation"""
    with pytest.raises(ValidationError):
        DeviceManifest(
            manifest_id=uuid4(),
            device_id="device-001",
            captured_at=datetime.now(timezone.utc),
            hardware=Hardware(
                cpu=CPU(model="Intel i7", cores=8, architecture="x86_64"),
                memory=Memory(total_bytes=16777216000),
            ),
            storage=Storage(devices=[]),
            os=OS(
                platform=Platform.LINUX,
                distribution="Ubuntu",
                kernel="5.15.0",
                architecture="x86_64",
            ),
            manifest_hash="invalid",  # Not a valid SHA-256 hash
        )


def test_cpu_cores_validation():
    """Test CPU cores must be positive"""
    with pytest.raises(ValidationError):
        CPU(model="Test", cores=0, architecture="x86_64")

    with pytest.raises(ValidationError):
        CPU(model="Test", cores=-1, architecture="x86_64")

