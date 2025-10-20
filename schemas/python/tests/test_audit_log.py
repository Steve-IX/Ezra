"""Tests for Audit Log schema"""

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from audit_log import (
    Actor,
    AuditDetails,
    AuditEvent,
    AuditLogEntry,
    AuditMetadata,
    create_audit_entry,
)


def test_audit_log_entry_creation():
    """Test creating an audit log entry"""
    entry = AuditLogEntry(
        entry_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        actor=Actor.AGENT,
        event=AuditEvent.STARTED,
        device_id="device-001",
    )
    assert entry.actor == Actor.AGENT
    assert entry.event == AuditEvent.STARTED


def test_audit_log_with_details():
    """Test audit log with details"""
    details = AuditDetails(
        command="apt-get install docker",
        output="Successfully installed",
        exit_code=0,
        duration_ms=5000,
        risk_level=3,
    )

    entry = AuditLogEntry(
        entry_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        actor=Actor.EXECUTOR,
        plan_id=uuid4(),
        step_id="step-1",
        event=AuditEvent.EXECUTED,
        details=details,
    )
    assert entry.details.exit_code == 0
    assert entry.details.duration_ms == 5000


def test_audit_log_with_error():
    """Test audit log with error details"""
    details = AuditDetails(
        command="invalid command",
        error="Command not found",
        exit_code=127,
        reason="Invalid command syntax",
    )

    entry = AuditLogEntry(
        entry_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        actor=Actor.AGENT,
        event=AuditEvent.ERROR,
        details=details,
    )
    assert entry.event == AuditEvent.ERROR
    assert entry.details.exit_code == 127


def test_audit_log_with_metadata():
    """Test audit log with metadata"""
    metadata = AuditMetadata(
        hostname="server-001",
        ip_address="192.168.1.100",
        agent_version="0.1.0",
        companion_version="0.1.0",
    )

    entry = AuditLogEntry(
        entry_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        actor=Actor.AGENT,
        event=AuditEvent.STARTED,
        metadata=metadata,
    )
    assert entry.metadata.hostname == "server-001"


def test_audit_log_event_types():
    """Test all audit event types"""
    events = [
        AuditEvent.PLANNED,
        AuditEvent.APPROVED,
        AuditEvent.REJECTED,
        AuditEvent.STARTED,
        AuditEvent.EXECUTING,
        AuditEvent.EXECUTED,
        AuditEvent.COMPLETED,
        AuditEvent.ROLLBACK_STARTED,
        AuditEvent.ROLLBACK_COMPLETED,
        AuditEvent.ERROR,
        AuditEvent.CANCELLED,
        AuditEvent.TIMEOUT,
    ]

    for event in events:
        entry = AuditLogEntry(
            entry_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            actor=Actor.AGENT,
            event=event,
        )
        assert entry.event == event


def test_audit_log_actor_types():
    """Test all actor types"""
    actors = [
        Actor.AGENT,
        Actor.EXECUTOR,
        Actor.USER,
        Actor.COMPANION,
        Actor.SYSTEM,
    ]

    for actor in actors:
        entry = AuditLogEntry(
            entry_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            actor=actor,
            event=AuditEvent.STARTED,
        )
        assert entry.actor == actor


def test_audit_log_with_checksum():
    """Test audit log with checksum for chain verification"""
    entry = AuditLogEntry(
        entry_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        actor=Actor.AGENT,
        event=AuditEvent.COMPLETED,
        checksum="a" * 64,  # SHA-256 of previous entry
    )
    assert entry.checksum == "a" * 64


def test_create_audit_entry_helper():
    """Test create_audit_entry helper function"""
    plan_id = uuid4()
    entry = create_audit_entry(
        actor=Actor.AGENT,
        event=AuditEvent.STARTED,
        plan_id=plan_id,
        step_id="step-1",
        details={"command": "test"},
        device_id="device-001",
    )
    assert entry.actor == Actor.AGENT
    assert entry.event == AuditEvent.STARTED
    assert entry.plan_id == plan_id
    assert entry.step_id == "step-1"
    assert entry.details.command == "test"


def test_audit_log_json_serialization():
    """Test JSON serialization and deserialization"""
    entry = AuditLogEntry(
        entry_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        actor=Actor.AGENT,
        plan_id=uuid4(),
        event=AuditEvent.EXECUTED,
        details=AuditDetails(
            command="test",
            exit_code=0,
        ),
    )

    # Serialize
    json_str = entry.model_dump_json()
    data = json.loads(json_str)

    # Deserialize
    entry2 = AuditLogEntry.model_validate(data)
    assert entry2.entry_id == entry.entry_id
    assert entry2.actor == entry.actor
    assert entry2.details.exit_code == 0


def test_audit_details_extra_fields():
    """Test that AuditDetails allows extra fields"""
    details = AuditDetails(
        command="test",
        custom_field="custom_value",  # Extra field
    )
    assert details.command == "test"
    # pydantic allows extra fields due to Config.extra = "allow"


def test_invalid_checksum_format():
    """Test invalid checksum format validation"""
    with pytest.raises(ValidationError):
        AuditLogEntry(
            entry_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            actor=Actor.AGENT,
            event=AuditEvent.STARTED,
            checksum="invalid",  # Not a valid SHA-256 hash
        )


def test_risk_level_validation():
    """Test risk level validation in details"""
    # Valid risk levels
    for risk in range(11):
        details = AuditDetails(risk_level=risk)
        assert details.risk_level == risk

    # Invalid risk levels
    with pytest.raises(ValidationError):
        AuditDetails(risk_level=-1)

    with pytest.raises(ValidationError):
        AuditDetails(risk_level=11)


def test_duration_validation():
    """Test duration must be non-negative"""
    details = AuditDetails(duration_ms=1000)
    assert details.duration_ms == 1000

    with pytest.raises(ValidationError):
        AuditDetails(duration_ms=-1)

