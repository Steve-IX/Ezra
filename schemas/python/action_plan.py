"""Action Plan Pydantic Models"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class StepType(str, Enum):
    """Step operation types"""

    PRECHECK = "precheck"
    UI = "ui"
    FS = "fs"
    INSTALL = "install"
    FLASH = "flash"
    FETCH = "fetch"
    CUSTOM = "custom"


class CheckCondition(BaseModel):
    """Pre or post condition for a step"""

    condition: str
    description: str


class Checks(BaseModel):
    """Pre and post checks for a step"""

    pre: Optional[list[CheckCondition]] = None
    post: Optional[list[CheckCondition]] = None


class Artifact(BaseModel):
    """Artifact to download or upload"""

    url: str
    sha256: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    size: int = Field(..., ge=0)
    destination: Optional[str] = None


class Step(BaseModel):
    """Action plan step"""

    id: str
    type: StepType
    description: str
    command: dict[str, Any]
    artifact: Optional[Artifact] = None
    checks: Optional[Checks] = None
    risk: int = Field(..., ge=0, le=10)
    requires_physical: bool = False
    estimated_duration: Optional[int] = Field(None, ge=0)
    dependencies: Optional[list[str]] = None


class RollbackStep(BaseModel):
    """Rollback step for reversing an action"""

    step_id: str
    description: str
    command: dict[str, Any]
    condition: Optional[str] = None


class TokenUsage(BaseModel):
    """LLM token usage statistics"""

    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)


class LLMProvider(str, Enum):
    """LLM provider types"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AUTO = "auto"


class ActionPlanMetadata(BaseModel):
    """Metadata about action plan generation"""

    llm_provider: LLMProvider
    model: str
    confidence: float = Field(..., ge=0, le=1)
    reasoning: Optional[str] = None
    token_usage: Optional[TokenUsage] = None


class ActionPlan(BaseModel):
    """Complete action plan with steps and rollback"""

    plan_id: UUID
    device_manifest_hash: str = Field(..., pattern=r"^[a-f0-9]{64}$")
    generated_by: str
    intent: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    steps: list[Step] = Field(..., min_length=1)
    rollback: list[RollbackStep]
    metadata: ActionPlanMetadata
    signature: Optional[str] = None

    @field_validator("device_manifest_hash")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        """Validate SHA-256 hash format"""
        if not v or len(v) != 64:
            msg = "device_manifest_hash must be a 64-character hex string"
            raise ValueError(msg)
        return v.lower()

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "plan_id": "550e8400-e29b-41d4-a716-446655440000",
                "device_manifest_hash": "a" * 64,
                "generated_by": "gpt-4",
                "intent": "Install Docker and configure development environment",
                "created_at": "2025-10-20T12:00:00Z",
                "steps": [
                    {
                        "id": "step-1",
                        "type": "precheck",
                        "description": "Check system requirements",
                        "command": {"check": "system_resources"},
                        "risk": 0,
                    },
                ],
                "rollback": [],
                "metadata": {
                    "llm_provider": "openai",
                    "model": "gpt-4",
                    "confidence": 0.95,
                },
            },
        }

