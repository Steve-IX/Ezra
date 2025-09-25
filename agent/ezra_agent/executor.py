"""Action plan executor with system adapters."""

import json
import subprocess
import time
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from .config import AgentConfig


class CommandExecutionError(Exception):
    """Custom exception for command execution errors."""


class ExecutionResult(BaseModel):
    """Execution result model."""

    action_id: str = Field(..., description="Action identifier")
    status: str = Field(..., description="Execution status")
    output: str = Field(default="", description="Command output")
    error: str | None = Field(None, description="Error message")
    duration: float = Field(..., description="Execution duration in seconds")
    timestamp: str = Field(..., description="Execution timestamp")


class ActionExecutor:
    """Executes action plans with system adapters."""

    def __init__(self, config: AgentConfig):
        """Initialize action executor."""
        self.config = config
        self.backup_dir = config.backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def execute_action_plan(self, action_plan: dict[str, Any]) -> list[ExecutionResult]:
        """Execute a complete action plan."""
        results = []
        actions = action_plan.get("actions", [])

        logger.info(f"Executing action plan with {len(actions)} actions")

        for action in actions:
            try:
                result = self.execute_action(action)
                results.append(result)

                # If action failed and is critical, stop execution
                if result.status == "failed" and action.get("risk_level") == "critical":
                    logger.error(
                        f"Critical action failed, stopping execution: {action.get('id')}"
                    )
                    break

            except (CommandExecutionError, ValueError, RuntimeError) as e:
                logger.error(f"Error executing action {action.get('id')}: {e}")
                results.append(ExecutionResult(
                    action_id=action.get("id", "unknown"),
                    status="failed",
                    error=str(e),
                    duration=0.0,
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                ))

        return results

    def execute_action(self, action: dict[str, Any]) -> ExecutionResult:
        """Execute a single action."""
        action_id = action.get("id", "unknown")
        action_type = action.get("type", "unknown")
        commands = action.get("commands", [])
        risk_level = action.get("risk_level", "medium")

        logger.info(f"Executing action {action_id} ({action_type}, {risk_level} risk)")

        start_time = time.time()

        try:
            # Create backup if high risk
            if risk_level in ["high", "critical"]:
                self._create_backup(action_id)

            # Execute commands
            output_lines = []
            for command in commands:
                logger.debug(f"Executing command: {command}")
                result = self._execute_command(command)
                output_lines.append(result)

            duration = time.time() - start_time
            output = "\n".join(output_lines)

            return ExecutionResult(
                action_id=action_id,
                status="completed",
                output=output,
                duration=duration,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )

        except (CommandExecutionError, ValueError, RuntimeError) as e:
            duration = time.time() - start_time
            logger.error(f"Action {action_id} failed: {e}")

            # Attempt rollback if available
            if "rollback_commands" in action:
                self._execute_rollback(action)

            return ExecutionResult(
                action_id=action_id,
                status="failed",
                error=str(e),
                duration=duration,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )

    def _execute_command(self, command: str) -> str:
        """Execute a single command."""
        try:
            # Use shell=True for cross-platform compatibility
            result = subprocess.run(
                command,
                check=False, shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"

            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, output)

            return output

        except subprocess.TimeoutExpired as e:
            msg = f"Command timed out: {command}"
            raise CommandExecutionError(msg) from e
        except subprocess.CalledProcessError as e:
            msg = f"Command failed with code {e.returncode}: {e.stderr}"
            raise CommandExecutionError(msg) from e

    def _create_backup(self, action_id: str) -> None:
        """Create backup before high-risk operations."""
        backup_path = self.backup_dir / f"{action_id}_{int(time.time())}.json"

        # Create a simple backup of current system state
        backup_data = {
            "action_id": action_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "system_info": self._get_system_info(),
        }

        with open(backup_path, "w") as f:
            json.dump(backup_data, f, indent=2)

        logger.info(f"Created backup: {backup_path}")

    def _execute_rollback(self, action: dict[str, Any]) -> None:
        """Execute rollback commands."""
        rollback_commands = action.get("rollback_commands", [])

        if not rollback_commands:
            logger.warning("No rollback commands available")
            return

        logger.info(f"Executing rollback for action {action.get('id')}")

        for command in rollback_commands:
            try:
                self._execute_command(command)
            except (CommandExecutionError, ValueError, RuntimeError) as e:
                logger.error(f"Rollback command failed: {command} - {e}")

    def _get_system_info(self) -> dict[str, Any]:
        """Get current system information for backup."""
        import platform

        import psutil

        return {
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage("/")._asdict() if platform.system() != "Windows" else psutil.disk_usage("C:\\")._asdict(),
        }
