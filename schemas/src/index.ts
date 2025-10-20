// Export all schemas and types
export * from './types';
export * from './crypto';
export * from './schemas';

// Re-export commonly used schemas for convenience (legacy)
export {
  DeviceInfoSchema,
  ActionPlanSchema as LegacyActionPlanSchema,
  ActionSchema,
  LLMRequestSchema,
  LLMResponseSchema,
  AgentRequestSchema,
  AgentResponseSchema,
  ExecutionResultSchema,
  CompanionConfigSchema,
  AgentConfigSchema,
} from './types';

export {
  SignatureSchema,
  SignedDataSchema,
  KeyPairSchema,
  CertificateSchema,
} from './crypto';

// Re-export new comprehensive schemas
export {
  ActionPlanSchema,
  DeviceManifestSchema,
  AuditLogEntrySchema,
  StepSchema,
  RollbackStepSchema,
} from './schemas';
