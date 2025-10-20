/**
 * Tests for Audit Log schema
 */

import {
  Actor,
  AuditEvent,
  AuditLogEntry,
  AuditLogEntrySchema,
} from '../schemas';

describe('AuditLogEntry Schema', () => {
  const validEntry: AuditLogEntry = {
    entry_id: '550e8400-e29b-41d4-a716-446655440000',
    timestamp: new Date().toISOString(),
    actor: 'agent' as Actor,
    event: 'started' as AuditEvent,
  };

  test('should validate a valid audit log entry', () => {
    const result = AuditLogEntrySchema.safeParse(validEntry);
    expect(result.success).toBe(true);
  });

  test('should validate all actor types', () => {
    const actors: Actor[] = ['agent', 'executor', 'user', 'companion', 'system'];
    actors.forEach((actor) => {
      const entry = { ...validEntry, actor };
      const result = AuditLogEntrySchema.safeParse(entry);
      expect(result.success).toBe(true);
    });
  });

  test('should validate all event types', () => {
    const events: AuditEvent[] = [
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
    ];
    events.forEach((event) => {
      const entry = { ...validEntry, event };
      const result = AuditLogEntrySchema.safeParse(entry);
      expect(result.success).toBe(true);
    });
  });

  test('should validate entry with details', () => {
    const entryWithDetails = {
      ...validEntry,
      details: {
        command: 'apt-get install docker',
        output: 'Successfully installed',
        exit_code: 0,
        duration_ms: 5000,
        risk_level: 3,
      },
    };
    const result = AuditLogEntrySchema.safeParse(entryWithDetails);
    expect(result.success).toBe(true);
  });

  test('should validate entry with error details', () => {
    const entryWithError = {
      ...validEntry,
      event: 'error' as AuditEvent,
      details: {
        command: 'invalid command',
        error: 'Command not found',
        exit_code: 127,
        reason: 'Invalid command syntax',
      },
    };
    const result = AuditLogEntrySchema.safeParse(entryWithError);
    expect(result.success).toBe(true);
  });

  test('should validate optional plan_id', () => {
    const entryWithPlan = {
      ...validEntry,
      plan_id: '660e8400-e29b-41d4-a716-446655440000',
      step_id: 'step-1',
    };
    const result = AuditLogEntrySchema.safeParse(entryWithPlan);
    expect(result.success).toBe(true);
  });

  test('should validate optional metadata', () => {
    const entryWithMetadata = {
      ...validEntry,
      metadata: {
        hostname: 'server-001',
        ip_address: '192.168.1.100',
        agent_version: '0.1.0',
      },
    };
    const result = AuditLogEntrySchema.safeParse(entryWithMetadata);
    expect(result.success).toBe(true);
  });

  test('should validate risk level range in details', () => {
    const validRisks = [0, 5, 10];
    validRisks.forEach((risk_level) => {
      const entry = {
        ...validEntry,
        details: { risk_level },
      };
      const result = AuditLogEntrySchema.safeParse(entry);
      expect(result.success).toBe(true);
    });

    const invalidRisks = [-1, 11];
    invalidRisks.forEach((risk_level) => {
      const entry = {
        ...validEntry,
        details: { risk_level },
      };
      const result = AuditLogEntrySchema.safeParse(entry);
      expect(result.success).toBe(false);
    });
  });

  test('should validate duration_ms is non-negative', () => {
    const validEntry1 = {
      ...validEntry,
      details: { duration_ms: 0 },
    };
    expect(AuditLogEntrySchema.safeParse(validEntry1).success).toBe(true);

    const invalidEntry = {
      ...validEntry,
      details: { duration_ms: -1 },
    };
    expect(AuditLogEntrySchema.safeParse(invalidEntry).success).toBe(false);
  });

  test('should validate checksum format', () => {
    const entryWithChecksum = {
      ...validEntry,
      checksum: 'a'.repeat(64),
    };
    const result = AuditLogEntrySchema.safeParse(entryWithChecksum);
    expect(result.success).toBe(true);

    const invalidChecksum = {
      ...validEntry,
      checksum: 'invalid',
    };
    expect(AuditLogEntrySchema.safeParse(invalidChecksum).success).toBe(false);
  });

  test('should validate device_manifest_hash format', () => {
    const entryWithHash = {
      ...validEntry,
      device_manifest_hash: 'b'.repeat(64),
    };
    const result = AuditLogEntrySchema.safeParse(entryWithHash);
    expect(result.success).toBe(true);

    const invalidHash = {
      ...validEntry,
      device_manifest_hash: 'short',
    };
    expect(AuditLogEntrySchema.safeParse(invalidHash).success).toBe(false);
  });

  test('should allow additional fields in details', () => {
    const entryWithExtra = {
      ...validEntry,
      details: {
        command: 'test',
        custom_field: 'custom_value',
      },
    };
    const result = AuditLogEntrySchema.safeParse(entryWithExtra);
    expect(result.success).toBe(true);
  });

  test('should serialize and deserialize correctly', () => {
    const entryWithDetails = {
      ...validEntry,
      plan_id: '660e8400-e29b-41d4-a716-446655440000',
      details: {
        command: 'test',
        exit_code: 0,
      },
    };
    const json = JSON.stringify(entryWithDetails);
    const parsed = JSON.parse(json);
    const result = AuditLogEntrySchema.safeParse(parsed);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.entry_id).toBe(entryWithDetails.entry_id);
    }
  });
});

