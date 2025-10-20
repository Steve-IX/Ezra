"""Audit Log Pydantic Models"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Actor(str, Enum):
    """Entity that performed an action"""

    AGENT = "agent"
    EXECUTOR = "executor"
    USER = "user"
    COMPANION = "companion"
    SYSTEM = "system"


class AuditEvent(str, Enum):
    """Type of audit event"""

    PLANNED = "planned"
    APPROVED = "approved"
    REJECTED = "rejected"
    STARTED = "started"
    EXECUTING = "executing"
    EXECUTED = "executed"
    COMPLETED = "completed"
    ROLLBACK_STARTED = "rollback_started"
    ROLLBACK_COMPLETED = "rollback_completed"
    ERROR = "error"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AuditDetails(BaseModel):
    """Event-specific details"""

    command: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    duration_ms: Optional[int] = Field(None, ge=0)
    risk_level: Optional[int] = Field(None, ge=0, le=10)
    backup_id: Optional[str] = None
    user_id: Optional[str] = None
    reason: Optional[str] = None

    class Config:
        """Pydantic config"""

        extra = "allow"  # Allow additional fields


class AuditMetadata(BaseModel):
    """Additional metadata"""

    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    agent_version: Optional[str] = None
    companion_version: Optional[str] = None

    class Config:
        """Pydantic config"""

        extra = "allow"  # Allow additional fields


class AuditLogEntry(BaseModel):
    """Audit log entry"""

    entry_id: UUID
    timestamp: datetime
    actor: Actor
    plan_id: Optional[UUID] = None
    step_id: Optional[str] = None
    event: AuditEvent
    details: Optional[AuditDetails] = None
    device_id: Optional[str] = None
    device_manifest_hash: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$")
    checksum: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$")
    metadata: Optional[AuditMetadata] = None

    class Config:
        """Pydantic config"""

        json_schema_extra = {
            "example": {
                "entry_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-10-20T12:00:00.123456Z",
                "actor": "agent",
                "plan_id": "660e8400-e29b-41d4-a716-446655440000",
                "step_id": "step-1",
                "event": "executed",
                "details": {
                    "command": "apt-get install docker",
                    "exit_code": 0,
                    "duration_ms": 5000,
                },
                "device_id": "device-001",
            },
        }


def create_audit_entry(
    actor: Actor,
    event: AuditEvent,
    *,
    plan_id: Optional[UUID] = None,
    step_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    device_id: Optional[str] = None,
    device_manifest_hash: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> AuditLogEntry:
    """Helper function to create audit log entries"""
    from uuid import uuid4

    return AuditLogEntry(
        entry_id=uuid4(),
        timestamp=datetime.utcnow(),
        actor=actor,
        plan_id=plan_id,
        step_id=step_id,
        event=event,
        details=AuditDetails(**details) if details else None,
        device_id=device_id,
        device_manifest_hash=device_manifest_hash,
        metadata=AuditMetadata(**metadata) if metadata else None,
    )

