/**
 * Tests for Device Manifest schema
 */

import {
  CPU,
  DeviceManifest,
  DeviceManifestSchema,
  Hardware,
  Memory,
  OS,
  Platform,
  Storage,
} from '../schemas';

describe('DeviceManifest Schema', () => {
  const validCPU: CPU = {
    model: 'Intel Core i7-9700K',
    cores: 8,
    architecture: 'x86_64',
  };

  const validMemory: Memory = {
    total_bytes: 16777216000,
  };

  const validHardware: Hardware = {
    cpu: validCPU,
    memory: validMemory,
  };

  const validOS: OS = {
    platform: 'linux' as Platform,
    distribution: 'Ubuntu',
    kernel: '5.15.0-76-generic',
    architecture: 'x86_64',
  };

  const validStorage: Storage = {
    devices: [
      {
        device: '/dev/sda',
        size_bytes: 512000000000,
      },
    ],
  };

  const validManifest: DeviceManifest = {
    manifest_id: '550e8400-e29b-41d4-a716-446655440000',
    device_id: 'device-001',
    captured_at: new Date().toISOString(),
    hardware: validHardware,
    storage: validStorage,
    os: validOS,
    manifest_hash: 'a'.repeat(64),
  };

  test('should validate a valid device manifest', () => {
    const result = DeviceManifestSchema.safeParse(validManifest);
    expect(result.success).toBe(true);
  });

  test('should require CPU cores to be positive', () => {
    const invalidCores = [0, -1];
    invalidCores.forEach((cores) => {
      const cpu = { ...validCPU, cores };
      const hardware = { ...validHardware, cpu };
      const result = DeviceManifestSchema.safeParse({
        ...validManifest,
        hardware,
      });
      expect(result.success).toBe(false);
    });
  });

  test('should validate platform enum', () => {
    const validPlatforms: Platform[] = ['linux', 'windows', 'android', 'console', 'unknown'];
    validPlatforms.forEach((platform) => {
      const os = { ...validOS, platform };
      const result = DeviceManifestSchema.safeParse({ ...validManifest, os });
      expect(result.success).toBe(true);
    });

    const invalidPlatform = 'invalid-platform';
    const result = DeviceManifestSchema.safeParse({
      ...validManifest,
      os: { ...validOS, platform: invalidPlatform as Platform },
    });
    expect(result.success).toBe(false);
  });

  test('should validate manifest_hash format', () => {
    const invalidHashes = ['short', 'g'.repeat(64), 'a'.repeat(63)];
    invalidHashes.forEach((hash) => {
      const result = DeviceManifestSchema.safeParse({
        ...validManifest,
        manifest_hash: hash,
      });
      expect(result.success).toBe(false);
    });
  });

  test('should allow optional GPU', () => {
    const hardwareWithGPU = {
      ...validHardware,
      gpu: {
        model: 'NVIDIA GTX 1080',
        vram_mb: 8192,
      },
    };
    const result = DeviceManifestSchema.safeParse({
      ...validManifest,
      hardware: hardwareWithGPU,
    });
    expect(result.success).toBe(true);
  });

  test('should validate storage devices', () => {
    const storage: Storage = {
      devices: [
        {
          device: '/dev/sda',
          type: 'ssd',
          size_bytes: 512000000000,
        },
        {
          device: '/dev/sdb',
          type: 'hdd',
          size_bytes: 1000000000000,
        },
      ],
    };
    const result = DeviceManifestSchema.safeParse({ ...validManifest, storage });
    expect(result.success).toBe(true);
  });

  test('should validate partitions', () => {
    const storage: Storage = {
      devices: [],
      partitions: [
        {
          device: '/dev/sda1',
          mount_point: '/',
          fstype: 'ext4',
          size_bytes: 100000000000,
          used_bytes: 50000000000,
        },
      ],
    };
    const result = DeviceManifestSchema.safeParse({ ...validManifest, storage });
    expect(result.success).toBe(true);
  });

  test('should validate optional packages array', () => {
    const manifestWithPackages = {
      ...validManifest,
      packages: [
        {
          name: 'docker',
          version: '24.0.5',
          manager: 'apt',
        },
        {
          name: 'nginx',
          version: '1.18.0',
          manager: 'apt',
        },
      ],
    };
    const result = DeviceManifestSchema.safeParse(manifestWithPackages);
    expect(result.success).toBe(true);
  });

  test('should validate optional boot configuration', () => {
    const manifestWithBoot = {
      ...validManifest,
      boot: {
        secure_boot_enabled: true,
        boot_loader: 'GRUB',
        uefi_mode: true,
        tpm_present: true,
      },
    };
    const result = DeviceManifestSchema.safeParse(manifestWithBoot);
    expect(result.success).toBe(true);
  });

  test('should validate optional firmware', () => {
    const manifestWithFirmware = {
      ...validManifest,
      firmware: {
        bios: {
          vendor: 'AMI',
          version: '1.2.3',
          release_date: '2023-01-15',
        },
      },
    };
    const result = DeviceManifestSchema.safeParse(manifestWithFirmware);
    expect(result.success).toBe(true);
  });

  test('should validate file info with sha256', () => {
    const manifestWithFiles = {
      ...validManifest,
      files: [
        {
          path: '/etc/passwd',
          sha256: 'b'.repeat(64),
          size_bytes: 2048,
        },
      ],
    };
    const result = DeviceManifestSchema.safeParse(manifestWithFiles);
    expect(result.success).toBe(true);
  });

  test('should serialize and deserialize correctly', () => {
    const json = JSON.stringify(validManifest);
    const parsed = JSON.parse(json);
    const result = DeviceManifestSchema.safeParse(parsed);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.device_id).toBe(validManifest.device_id);
    }
  });
});

