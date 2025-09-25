import { z } from 'zod';

// Device information schema
export const DeviceInfoSchema = z.object({
  id: z.string(),
  platform: z.enum(['linux', 'windows', 'android', 'console']),
  architecture: z.string(),
  os: z.string(),
  version: z.string(),
  hardware: z.object({
    cpu: z.string(),
    memory: z.number(),
    storage: z.number(),
    gpu: z.string().optional(),
  }),
  capabilities: z.array(z.string()),
  timestamp: z.string(),
});

export type DeviceInfo = z.infer<typeof DeviceInfoSchema>;

// Action plan schema
export const ActionSchema = z.object({
  id: z.string(),
  type: z.enum(['install', 'configure', 'modify', 'backup', 'restore', 'jailbreak', 'bypass']),
  description: z.string(),
  risk_level: z.enum(['low', 'medium', 'high', 'critical']),
  requires_consent: z.boolean(),
  commands: z.array(z.string()),
  rollback_commands: z.array(z.string()).optional(),
  dependencies: z.array(z.string()).optional(),
  estimated_duration: z.number().optional(), // seconds
});

export const ActionPlanSchema = z.object({
  id: z.string(),
  device_id: z.string(),
  created_at: z.string(),
  expires_at: z.string(),
  actions: z.array(ActionSchema),
  signature: z.string(),
  metadata: z.object({
    llm_provider: z.string(),
    model: z.string(),
    confidence: z.number().min(0).max(1),
    reasoning: z.string(),
  }),
});

export type Action = z.infer<typeof ActionSchema>;
export type ActionPlan = z.infer<typeof ActionPlanSchema>;

// LLM provider schemas
export const LLMProviderSchema = z.enum(['openai', 'anthropic', 'google']);
export type LLMProvider = z.infer<typeof LLMProviderSchema>;

export const LLMRequestSchema = z.object({
  provider: LLMProviderSchema,
  model: z.string(),
  prompt: z.string(),
  max_tokens: z.number().optional(),
  temperature: z.number().min(0).max(2).optional(),
  system_prompt: z.string().optional(),
});

export const LLMResponseSchema = z.object({
  provider: LLMProviderSchema,
  model: z.string(),
  content: z.string(),
  usage: z.object({
    prompt_tokens: z.number(),
    completion_tokens: z.number(),
    total_tokens: z.number(),
  }),
  metadata: z.object({
    finish_reason: z.string(),
    confidence: z.number().min(0).max(1).optional(),
  }),
});

export type LLMRequest = z.infer<typeof LLMRequestSchema>;
export type LLMResponse = z.infer<typeof LLMResponseSchema>;

// Agent communication schemas
export const AgentRequestSchema = z.object({
  device_info: DeviceInfoSchema,
  user_prompt: z.string(),
  context: z.object({
    previous_actions: z.array(z.string()).optional(),
    user_preferences: z.record(z.any()).optional(),
    constraints: z.array(z.string()).optional(),
  }).optional(),
});

export const AgentResponseSchema = z.object({
  action_plan: ActionPlanSchema,
  human_readable_summary: z.string(),
  consent_required: z.boolean(),
  estimated_risk: z.enum(['low', 'medium', 'high', 'critical']),
});

export type AgentRequest = z.infer<typeof AgentRequestSchema>;
export type AgentResponse = z.infer<typeof AgentResponseSchema>;

// Execution status schemas
export const ExecutionStatusSchema = z.enum(['pending', 'running', 'completed', 'failed', 'cancelled']);
export type ExecutionStatus = z.infer<typeof ExecutionStatusSchema>;

export const ExecutionResultSchema = z.object({
  action_id: z.string(),
  status: ExecutionStatusSchema,
  output: z.string(),
  error: z.string().optional(),
  duration: z.number(),
  timestamp: z.string(),
});

export type ExecutionResult = z.infer<typeof ExecutionResultSchema>;

// Configuration schemas
export const CompanionConfigSchema = z.object({
  port: z.number().default(3000),
  host: z.string().default('0.0.0.0'),
  llm_providers: z.object({
    openai: z.object({
      api_key: z.string(),
      models: z.array(z.string()).default(['gpt-4', 'gpt-3.5-turbo']),
    }).optional(),
    anthropic: z.object({
      api_key: z.string(),
      models: z.array(z.string()).default(['claude-3-opus', 'claude-3-sonnet']),
    }).optional(),
    google: z.object({
      api_key: z.string(),
      models: z.array(z.string()).default(['gemini-pro']),
    }).optional(),
  }),
  signing: z.object({
    private_key: z.string(),
    public_key: z.string(),
  }),
  rate_limits: z.object({
    requests_per_minute: z.number().default(60),
    tokens_per_minute: z.number().default(100000),
  }),
});

export type CompanionConfig = z.infer<typeof CompanionConfigSchema>;

export const AgentConfigSchema = z.object({
  companion_url: z.string(),
  device_id: z.string(),
  polling_interval: z.number().default(5000), // ms
  max_retries: z.number().default(3),
  timeout: z.number().default(30000), // ms
  log_level: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

export type AgentConfig = z.infer<typeof AgentConfigSchema>;
