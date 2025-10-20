/**
 * Comprehensive Zod schemas for Ezra
 * Generated from JSON Schema definitions
 */

import { z } from 'zod';

// ============================================================
// Action Plan Schemas
// ============================================================

export const StepTypeSchema = z.enum([
  'precheck',
  'ui',
  'fs',
  'install',
  'flash',
  'fetch',
  'custom',
]);

export const CheckConditionSchema = z.object({
  condition: z.string(),
  description: z.string(),
});

export const ChecksSchema = z.object({
  pre: z.array(CheckConditionSchema).optional(),
  post: z.array(CheckConditionSchema).optional(),
});

export const ArtifactSchema = z.object({
  url: z.string().url(),
  sha256: z.string().regex(/^[a-f0-9]{64}$/),
  size: z.number().int().nonnegative(),
  destination: z.string().optional(),
});

export const StepSchema = z.object({
  id: z.string(),
  type: StepTypeSchema,
  description: z.string(),
  command: z.record(z.any()),
  artifact: ArtifactSchema.optional(),
  checks: ChecksSchema.optional(),
  risk: z.number().int().min(0).max(10),
  requires_physical: z.boolean().default(false),
  estimated_duration: z.number().int().nonnegative().optional(),
  dependencies: z.array(z.string()).optional(),
});

export const RollbackStepSchema = z.object({
  step_id: z.string(),
  description: z.string(),
  command: z.record(z.any()),
  condition: z.string().optional(),
});

export const TokenUsageSchema = z.object({
  prompt_tokens: z.number().int().nonnegative(),
  completion_tokens: z.number().int().nonnegative(),
  total_tokens: z.number().int().nonnegative(),
});

export const ActionPlanMetadataSchema = z.object({
  llm_provider: z.enum(['openai', 'anthropic', 'google', 'auto']),
  model: z.string(),
  confidence: z.number().min(0).max(1),
  reasoning: z.string().optional(),
  token_usage: TokenUsageSchema.optional(),
});

export const ActionPlanSchema = z.object({
  plan_id: z.string().uuid(),
  device_manifest_hash: z.string().regex(/^[a-f0-9]{64}$/),
  generated_by: z.string(),
  intent: z.string(),
  created_at: z.string().datetime(),
  expires_at: z.string().datetime().optional(),
  steps: z.array(StepSchema).min(1),
  rollback: z.array(RollbackStepSchema),
  metadata: ActionPlanMetadataSchema,
  signature: z.string().optional(),
});

export type StepType = z.infer<typeof StepTypeSchema>;
export type CheckCondition = z.infer<typeof CheckConditionSchema>;
export type Checks = z.infer<typeof ChecksSchema>;
export type Artifact = z.infer<typeof ArtifactSchema>;
export type Step = z.infer<typeof StepSchema>;
export type RollbackStep = z.infer<typeof RollbackStepSchema>;
export type TokenUsage = z.infer<typeof TokenUsageSchema>;
export type ActionPlanMetadata = z.infer<typeof ActionPlanMetadataSchema>;
export type ActionPlan = z.infer<typeof ActionPlanSchema>;

// ============================================================
// Device Manifest Schemas
// ============================================================

export const CPUSchema = z.object({
  model: z.string(),
  vendor: z.string().optional(),
  cores: z.number().int().positive(),
  threads: z.number().int().positive().optional(),
  frequency_mhz: z.number().int().nonnegative().optional(),
  architecture: z.string(),
});

export const GPUSchema = z.object({
  model: z.string(),
  vendor: z.string().optional(),
  vram_mb: z.number().int().nonnegative().optional(),
  driver_version: z.string().optional(),
});

export const MemorySchema = z.object({
  total_bytes: z.number().int().nonnegative(),
  available_bytes: z.number().int().nonnegative().optional(),
  swap_total_bytes: z.number().int().nonnegative().optional(),
  swap_used_bytes: z.number().int().nonnegative().optional(),
});

export const HardwareSchema = z.object({
  cpu: CPUSchema,
  gpu: GPUSchema.optional(),
  memory: MemorySchema,
  chipset: z.string().optional(),
});

export const StorageDeviceTypeSchema = z.enum([
  'hdd',
  'ssd',
  'nvme',
  'emmc',
  'sd',
  'usb',
  'unknown',
]);

export const StorageDeviceSchema = z.object({
  device: z.string(),
  model: z.string().optional(),
  type: StorageDeviceTypeSchema.optional(),
  size_bytes: z.number().int().nonnegative(),
});

export const PartitionSchema = z.object({
  device: z.string(),
  mount_point: z.string(),
  fstype: z.string(),
  size_bytes: z.number().int().nonnegative(),
  used_bytes: z.number().int().nonnegative().optional(),
  uuid: z.string().optional(),
  label: z.string().optional(),
});

export const StorageSchema = z.object({
  devices: z.array(StorageDeviceSchema),
  partitions: z.array(PartitionSchema).optional(),
});

export const BootSchema = z.object({
  secure_boot_enabled: z.boolean().optional(),
  boot_loader: z.string().optional(),
  boot_loader_version: z.string().optional(),
  boot_hash: z.string().regex(/^[a-f0-9]{64}$/).optional(),
  uefi_mode: z.boolean().optional(),
  tpm_present: z.boolean().optional(),
  tpm_version: z.string().optional(),
});

export const BIOSSchema = z.object({
  vendor: z.string().optional(),
  version: z.string().optional(),
  release_date: z.string().optional(),
});

export const FirmwareSchema = z.object({
  bios: BIOSSchema.optional(),
  ec_version: z.string().optional(),
  me_version: z.string().optional(),
});

export const PlatformSchema = z.enum([
  'linux',
  'windows',
  'android',
  'console',
  'unknown',
]);

export const SELinuxStatusSchema = z.enum([
  'enforcing',
  'permissive',
  'disabled',
  'not_present',
]);

export const OSSchema = z.object({
  platform: PlatformSchema,
  distribution: z.string(),
  version: z.string().optional(),
  kernel: z.string(),
  architecture: z.string(),
  init_system: z.string().optional(),
  selinux_status: SELinuxStatusSchema.optional(),
  apparmor_enabled: z.boolean().optional(),
});

export const PackageManagerSchema = z.enum([
  'apt',
  'yum',
  'dnf',
  'pacman',
  'zypper',
  'apk',
  'choco',
  'winget',
  'pip',
  'npm',
  'cargo',
  'unknown',
]);

export const PackageSchema = z.object({
  name: z.string(),
  version: z.string(),
  manager: PackageManagerSchema,
  architecture: z.string().optional(),
});

export const FileInfoSchema = z.object({
  path: z.string(),
  sha256: z.string().regex(/^[a-f0-9]{64}$/),
  size_bytes: z.number().int().nonnegative().optional(),
  permissions: z.string().optional(),
  owner: z.string().optional(),
});

export const LogsSchema = z.object({
  dmesg: z.array(z.string()).optional(),
  syslog: z.array(z.string()).optional(),
  journal: z.array(z.string()).optional(),
});

export const DeviceManifestSchema = z.object({
  manifest_id: z.string().uuid(),
  device_id: z.string(),
  captured_at: z.string().datetime(),
  hardware: HardwareSchema,
  storage: StorageSchema,
  boot: BootSchema.optional(),
  firmware: FirmwareSchema.optional(),
  os: OSSchema,
  packages: z.array(PackageSchema).optional(),
  files: z.array(FileInfoSchema).optional(),
  logs: LogsSchema.optional(),
  capabilities: z.array(z.string()).optional(),
  manifest_hash: z.string().regex(/^[a-f0-9]{64}$/),
});

export type CPU = z.infer<typeof CPUSchema>;
export type GPU = z.infer<typeof GPUSchema>;
export type Memory = z.infer<typeof MemorySchema>;
export type Hardware = z.infer<typeof HardwareSchema>;
export type StorageDeviceType = z.infer<typeof StorageDeviceTypeSchema>;
export type StorageDevice = z.infer<typeof StorageDeviceSchema>;
export type Partition = z.infer<typeof PartitionSchema>;
export type Storage = z.infer<typeof StorageSchema>;
export type Boot = z.infer<typeof BootSchema>;
export type BIOS = z.infer<typeof BIOSSchema>;
export type Firmware = z.infer<typeof FirmwareSchema>;
export type Platform = z.infer<typeof PlatformSchema>;
export type SELinuxStatus = z.infer<typeof SELinuxStatusSchema>;
export type OS = z.infer<typeof OSSchema>;
export type PackageManager = z.infer<typeof PackageManagerSchema>;
export type Package = z.infer<typeof PackageSchema>;
export type FileInfo = z.infer<typeof FileInfoSchema>;
export type Logs = z.infer<typeof LogsSchema>;
export type DeviceManifest = z.infer<typeof DeviceManifestSchema>;

// ============================================================
// Audit Log Schemas
// ============================================================

export const ActorSchema = z.enum(['agent', 'executor', 'user', 'companion', 'system']);

export const AuditEventSchema = z.enum([
  'planned',
  'approved',
  'rejected',
  'started',
  'executing',
  'executed',
  'completed',
  'rollback_started',
  'rollback_completed',
  'error',
  'cancelled',
  'timeout',
]);

export const AuditDetailsSchema = z.object({
  command: z.string().optional(),
  output: z.string().optional(),
  error: z.string().optional(),
  exit_code: z.number().int().optional(),
  duration_ms: z.number().int().nonnegative().optional(),
  risk_level: z.number().int().min(0).max(10).optional(),
  backup_id: z.string().optional(),
  user_id: z.string().optional(),
  reason: z.string().optional(),
}).passthrough();

export const AuditMetadataSchema = z.object({
  hostname: z.string().optional(),
  ip_address: z.string().optional(),
  agent_version: z.string().optional(),
  companion_version: z.string().optional(),
}).passthrough();

export const AuditLogEntrySchema = z.object({
  entry_id: z.string().uuid(),
  timestamp: z.string().datetime(),
  actor: ActorSchema,
  plan_id: z.string().uuid().optional(),
  step_id: z.string().optional(),
  event: AuditEventSchema,
  details: AuditDetailsSchema.optional(),
  device_id: z.string().optional(),
  device_manifest_hash: z.string().regex(/^[a-f0-9]{64}$/).optional(),
  checksum: z.string().regex(/^[a-f0-9]{64}$/).optional(),
  metadata: AuditMetadataSchema.optional(),
});

export type Actor = z.infer<typeof ActorSchema>;
export type AuditEvent = z.infer<typeof AuditEventSchema>;
export type AuditDetails = z.infer<typeof AuditDetailsSchema>;
export type AuditMetadata = z.infer<typeof AuditMetadataSchema>;
export type AuditLogEntry = z.infer<typeof AuditLogEntrySchema>;

