/**
 * Tests for Action Plan schema
 */

import {
  ActionPlan,
  ActionPlanMetadata,
  ActionPlanSchema,
  Artifact,
  RollbackStep,
  Step,
  StepType,
} from '../schemas';

describe('ActionPlan Schema', () => {
  const validStep: Step = {
    id: 'step-1',
    type: 'precheck' as StepType,
    description: 'Check system requirements',
    command: { check: 'memory' },
    risk: 1,
    requires_physical: false,
  };

  const validMetadata: ActionPlanMetadata = {
    llm_provider: 'openai',
    model: 'gpt-4',
    confidence: 0.95,
  };

  const validPlan: ActionPlan = {
    plan_id: '550e8400-e29b-41d4-a716-446655440000',
    device_manifest_hash: 'a'.repeat(64),
    generated_by: 'gpt-4',
    intent: 'Install Docker',
    created_at: new Date().toISOString(),
    steps: [validStep],
    rollback: [],
    metadata: validMetadata,
  };

  test('should validate a valid action plan', () => {
    const result = ActionPlanSchema.safeParse(validPlan);
    expect(result.success).toBe(true);
  });

  test('should require at least one step', () => {
    const invalidPlan = { ...validPlan, steps: [] };
    const result = ActionPlanSchema.safeParse(invalidPlan);
    expect(result.success).toBe(false);
  });

  test('should validate step risk range (0-10)', () => {
    const validRisks = [0, 1, 5, 10];
    validRisks.forEach((risk) => {
      const step = { ...validStep, risk };
      expect(() => ActionPlanSchema.parse({ ...validPlan, steps: [step] })).not.toThrow();
    });

    const invalidRisks = [-1, 11, 100];
    invalidRisks.forEach((risk) => {
      const step = { ...validStep, risk };
      const result = ActionPlanSchema.safeParse({ ...validPlan, steps: [step] });
      expect(result.success).toBe(false);
    });
  });

  test('should validate device_manifest_hash format', () => {
    const invalidHashes = ['short', 'g'.repeat(64), 'a'.repeat(63), 'a'.repeat(65)];
    invalidHashes.forEach((hash) => {
      const result = ActionPlanSchema.safeParse({
        ...validPlan,
        device_manifest_hash: hash,
      });
      expect(result.success).toBe(false);
    });
  });

  test('should validate step types', () => {
    const validTypes: StepType[] = ['precheck', 'ui', 'fs', 'install', 'flash', 'fetch', 'custom'];
    validTypes.forEach((type) => {
      const step = { ...validStep, type };
      expect(() => ActionPlanSchema.parse({ ...validPlan, steps: [step] })).not.toThrow();
    });
  });

  test('should validate artifact with sha256', () => {
    const artifact: Artifact = {
      url: 'https://example.com/pkg.tar.gz',
      sha256: 'b'.repeat(64),
      size: 1024,
    };
    const stepWithArtifact = { ...validStep, artifact };
    const result = ActionPlanSchema.safeParse({ ...validPlan, steps: [stepWithArtifact] });
    expect(result.success).toBe(true);
  });

  test('should validate rollback steps', () => {
    const rollback: RollbackStep = {
      step_id: 'step-1',
      description: 'Rollback installation',
      command: { uninstall: 'package' },
    };
    const result = ActionPlanSchema.safeParse({ ...validPlan, rollback: [rollback] });
    expect(result.success).toBe(true);
  });

  test('should validate confidence range (0-1)', () => {
    const validConfidences = [0, 0.5, 0.95, 1];
    validConfidences.forEach((confidence) => {
      const metadata = { ...validMetadata, confidence };
      const result = ActionPlanSchema.safeParse({ ...validPlan, metadata });
      expect(result.success).toBe(true);
    });

    const invalidConfidences = [-0.1, 1.1, 2];
    invalidConfidences.forEach((confidence) => {
      const metadata = { ...validMetadata, confidence };
      const result = ActionPlanSchema.safeParse({ ...validPlan, metadata });
      expect(result.success).toBe(false);
    });
  });

  test('should allow optional signature field', () => {
    const planWithSignature = { ...validPlan, signature: 'base64signature==' };
    const result = ActionPlanSchema.safeParse(planWithSignature);
    expect(result.success).toBe(true);
  });

  test('should validate UUID format for plan_id', () => {
    const invalidUUIDs = ['not-a-uuid', '123', 'g50e8400-e29b-41d4-a716-446655440000'];
    invalidUUIDs.forEach((plan_id) => {
      const result = ActionPlanSchema.safeParse({ ...validPlan, plan_id });
      expect(result.success).toBe(false);
    });
  });

  test('should serialize and deserialize correctly', () => {
    const json = JSON.stringify(validPlan);
    const parsed = JSON.parse(json);
    const result = ActionPlanSchema.safeParse(parsed);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.intent).toBe(validPlan.intent);
    }
  });
});

