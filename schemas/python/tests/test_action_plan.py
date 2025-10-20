"""Tests for Action Plan schema"""

import json
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from action_plan import (
    ActionPlan,
    ActionPlanMetadata,
    Artifact,
    LLMProvider,
    RollbackStep,
    Step,
    StepType,
    TokenUsage,
)


def test_step_creation():
    """Test creating a valid step"""
    step = Step(
        id="step-1",
        type=StepType.PRECHECK,
        description="Check system requirements",
        command={"check": "memory"},
        risk=1,
    )
    assert step.id == "step-1"
    assert step.type == StepType.PRECHECK
    assert step.risk == 1
    assert step.requires_physical is False


def test_step_with_artifact():
    """Test step with artifact"""
    step = Step(
        id="step-1",
        type=StepType.FETCH,
        description="Download package",
        command={"url": "https://example.com/pkg"},
        risk=2,
        artifact=Artifact(
            url="https://example.com/pkg.tar.gz",
            sha256="a" * 64,
            size=1024,
            destination="/tmp/pkg.tar.gz",
        ),
    )
    assert step.artifact is not None
    assert step.artifact.size == 1024


def test_step_risk_validation():
    """Test risk level validation"""
    # Valid risk levels
    for risk in range(11):
        step = Step(
            id=f"step-{risk}",
            type=StepType.CUSTOM,
            description=f"Risk {risk}",
            command={},
            risk=risk,
        )
        assert step.risk == risk

    # Invalid risk levels
    with pytest.raises(ValidationError):
        Step(
            id="invalid",
            type=StepType.CUSTOM,
            description="Invalid",
            command={},
            risk=-1,
        )

    with pytest.raises(ValidationError):
        Step(
            id="invalid",
            type=StepType.CUSTOM,
            description="Invalid",
            command={},
            risk=11,
        )


def test_rollback_step():
    """Test rollback step creation"""
    rollback = RollbackStep(
        step_id="step-1",
        description="Rollback installation",
        command={"uninstall": "package"},
    )
    assert rollback.step_id == "step-1"


def test_action_plan_metadata():
    """Test action plan metadata"""
    metadata = ActionPlanMetadata(
        llm_provider=LLMProvider.OPENAI,
        model="gpt-4",
        confidence=0.95,
        reasoning="Based on system analysis",
        token_usage=TokenUsage(
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
        ),
    )
    assert metadata.confidence == 0.95
    assert metadata.token_usage.total_tokens == 300


def test_action_plan_creation():
    """Test creating a complete action plan"""
    plan = ActionPlan(
        plan_id=uuid4(),
        device_manifest_hash="a" * 64,
        generated_by="gpt-4",
        intent="Install Docker",
        created_at=datetime.now(timezone.utc),
        steps=[
            Step(
                id="step-1",
                type=StepType.PRECHECK,
                description="Check requirements",
                command={"check": "memory"},
                risk=0,
            ),
            Step(
                id="step-2",
                type=StepType.INSTALL,
                description="Install Docker",
                command={"package": "docker"},
                risk=3,
            ),
        ],
        rollback=[
            RollbackStep(
                step_id="step-2",
                description="Uninstall Docker",
                command={"uninstall": "docker"},
            ),
        ],
        metadata=ActionPlanMetadata(
            llm_provider=LLMProvider.OPENAI,
            model="gpt-4",
            confidence=0.95,
        ),
    )
    assert len(plan.steps) == 2
    assert len(plan.rollback) == 1
    assert plan.metadata.llm_provider == LLMProvider.OPENAI


def test_action_plan_validation():
    """Test action plan validation"""
    # Must have at least one step
    with pytest.raises(ValidationError):
        ActionPlan(
            plan_id=uuid4(),
            device_manifest_hash="a" * 64,
            generated_by="gpt-4",
            intent="Test",
            created_at=datetime.now(timezone.utc),
            steps=[],  # Empty steps array
            rollback=[],
            metadata=ActionPlanMetadata(
                llm_provider=LLMProvider.OPENAI,
                model="gpt-4",
                confidence=0.95,
            ),
        )


def test_action_plan_json_serialization():
    """Test JSON serialization and deserialization"""
    plan = ActionPlan(
        plan_id=uuid4(),
        device_manifest_hash="a" * 64,
        generated_by="gpt-4",
        intent="Install Docker",
        created_at=datetime.now(timezone.utc),
        steps=[
            Step(
                id="step-1",
                type=StepType.INSTALL,
                description="Install",
                command={"pkg": "docker"},
                risk=3,
            ),
        ],
        rollback=[],
        metadata=ActionPlanMetadata(
            llm_provider=LLMProvider.OPENAI,
            model="gpt-4",
            confidence=0.95,
        ),
    )

    # Serialize
    json_str = plan.model_dump_json()
    data = json.loads(json_str)

    # Deserialize
    plan2 = ActionPlan.model_validate(data)
    assert plan2.plan_id == plan.plan_id
    assert plan2.intent == plan.intent
    assert len(plan2.steps) == 1


def test_invalid_hash_format():
    """Test invalid hash format validation"""
    with pytest.raises(ValidationError):
        ActionPlan(
            plan_id=uuid4(),
            device_manifest_hash="invalid",  # Not a valid SHA-256 hash
            generated_by="gpt-4",
            intent="Test",
            created_at=datetime.now(timezone.utc),
            steps=[
                Step(
                    id="step-1",
                    type=StepType.CUSTOM,
                    description="Test",
                    command={},
                    risk=0,
                ),
            ],
            rollback=[],
            metadata=ActionPlanMetadata(
                llm_provider=LLMProvider.OPENAI,
                model="gpt-4",
                confidence=0.95,
            ),
        )

