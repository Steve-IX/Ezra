# @ezra/schemas

Comprehensive schema definitions and validation models for the Ezra project, available in both TypeScript and Python.

## Overview

This package provides three core schemas:

1. **Action Plan** - Describes operations to be executed on a device
2. **Device Manifest** - Captures comprehensive device state (hardware, OS, firmware, packages)
3. **Audit Log** - Records all operations for compliance and debugging

## Installation

### TypeScript/JavaScript

```bash
pnpm add @ezra/schemas
# or
npm install @ezra/schemas
```

### Python

```bash
cd schemas/python
pip install -e .
```

## Usage

### TypeScript

```typescript
import {
  ActionPlanSchema,
  DeviceManifestSchema,
  AuditLogEntrySchema,
  type ActionPlan,
  type DeviceManifest,
  type AuditLogEntry,
} from '@ezra/schemas';

// Validate an action plan
const plan: ActionPlan = {
  plan_id: '550e8400-e29b-41d4-a716-446655440000',
  device_manifest_hash: 'a'.repeat(64),
  generated_by: 'gpt-4',
  intent: 'Install Docker',
  created_at: new Date().toISOString(),
  steps: [
    {
      id: 'step-1',
      type: 'install',
      description: 'Install Docker',
      command: { package: 'docker' },
      risk: 3,
    },
  ],
  rollback: [],
  metadata: {
    llm_provider: 'openai',
    model: 'gpt-4',
    confidence: 0.95,
  },
};

// Validate with Zod
const result = ActionPlanSchema.safeParse(plan);
if (result.success) {
  console.log('Valid plan:', result.data);
} else {
  console.error('Validation errors:', result.error);
}
```

### Python

```python
from datetime import datetime
from uuid import uuid4

from action_plan import ActionPlan, ActionPlanMetadata, Step, StepType, LLMProvider

# Create an action plan
plan = ActionPlan(
    plan_id=uuid4(),
    device_manifest_hash='a' * 64,
    generated_by='gpt-4',
    intent='Install Docker',
    created_at=datetime.utcnow(),
    steps=[
        Step(
            id='step-1',
            type=StepType.INSTALL,
            description='Install Docker',
            command={'package': 'docker'},
            risk=3,
        )
    ],
    rollback=[],
    metadata=ActionPlanMetadata(
        llm_provider=LLMProvider.OPENAI,
        model='gpt-4',
        confidence=0.95,
    ),
)

# Serialize to JSON
json_str = plan.model_dump_json(indent=2)

# Deserialize from dict
data = plan.model_dump()
plan2 = ActionPlan.model_validate(data)
```

## Schema Details

### Action Plan

An action plan describes a series of steps to execute on a device:

- **Core Fields**: `plan_id`, `device_manifest_hash`, `generated_by`, `intent`, `created_at`
- **Steps**: Array of operations with type, description, command, risk level (0-10)
- **Rollback**: Reverse operations for each step
- **Metadata**: LLM provider info, model, confidence score, token usage
- **Signature**: Ed25519 detached signature (added by companion server)

#### Step Types

- `precheck` - Validate preconditions
- `ui` - User interface interactions
- `fs` - File system operations
- `install` - Package installations
- `flash` - Firmware/ROM flashing
- `fetch` - Download artifacts
- `custom` - Custom operations

### Device Manifest

Comprehensive snapshot of device state:

- **Hardware**: CPU (model, cores, frequency), GPU, Memory, Chipset
- **Storage**: Devices, partitions, mount points, file systems
- **Boot**: Secure boot status, bootloader, TPM information
- **Firmware**: BIOS/UEFI version, EC version, ME version
- **OS**: Platform, distribution, kernel, architecture, security status
- **Packages**: Installed packages with versions and managers
- **Files**: Critical system files with SHA-256 hashes
- **Logs**: Recent log tails (dmesg, syslog, journal)
- **manifest_hash**: SHA-256 of entire manifest for integrity

### Audit Log

Append-only audit trail for all operations:

- **Entry ID**: Unique UUID for each log entry
- **Timestamp**: ISO 8601 with microsecond precision
- **Actor**: Who performed the action (agent|executor|user|companion|system)
- **Event**: Type of event (planned|approved|executed|error|rollback|etc.)
- **Details**: Command, output, error, exit code, duration, risk level
- **Checksum**: Optional SHA-256 linking to previous entry for tamper detection

## JSON Schema Files

The package includes JSON Schema files for validation and documentation:

- `src/action-plan.schema.json`
- `src/device-manifest.schema.json`
- `src/audit-log.schema.json`

These can be used with any JSON Schema validator or for generating types in other languages.

## Testing

### TypeScript

```bash
cd schemas
pnpm test
```

### Python

```bash
cd schemas/python
pytest tests/
```

## Development

### Build TypeScript

```bash
cd schemas
pnpm build
```

### Lint

```bash
pnpm lint
```

### Watch Mode

```bash
pnpm test:watch
```

## Cross-Language Compatibility

The schemas are designed to be compatible across TypeScript and Python:

1. JSON generated from TypeScript can be validated by Python models
2. JSON generated from Python can be validated by TypeScript schemas
3. All date-times use ISO 8601 format
4. All UUIDs use standard UUID format
5. All hashes use lowercase hexadecimal

## License

MIT - See LICENSE file for details.

