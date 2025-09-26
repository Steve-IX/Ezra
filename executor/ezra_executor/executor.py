"""Main executor engine."""

import time
from typing import Any

from loguru import logger

from .adapters import AndroidAdapter, BaseAdapter, LinuxAdapter, WindowsAdapter
from .adapters.base import ExecutionResult


class ExecutorEngine:
    """Main executor engine for running actions."""

    def __init__(self):
        """Initialize executor engine."""
        self.adapters: dict[str, type[BaseAdapter]] = {
            "linux": LinuxAdapter,
            "windows": WindowsAdapter,
            "android": AndroidAdapter,
        }
        self._current_adapter: BaseAdapter | None = None

    def get_adapter(self, platform: str) -> BaseAdapter:
        """Get adapter for the specified platform."""
        if self._current_adapter is None or self._current_adapter.get_platform() != platform:
            adapter_class = self.adapters.get(platform)
            if not adapter_class:
                raise ValueError(f"Unsupported platform: {platform}")

            self._current_adapter = adapter_class()

        return self._current_adapter

    def execute_action_plan(self, action_plan: dict[str, Any]) -> list[ExecutionResult]:
        """Execute a complete action plan."""
        platform = action_plan.get("platform", "linux")
        actions = action_plan.get("actions", [])

        logger.info(f"Executing action plan on {platform} with {len(actions)} actions")

        adapter = self.get_adapter(platform)
        results = []

        for action in actions:
            try:
                result = self.execute_action(adapter, action)
                results.append(result)

                # If action failed and is critical, stop execution
                if result.success is False and action.get("risk_level") == "critical":
                    logger.error(f"Critical action failed, stopping execution: {action.get('id')}")
                    break

            except Exception as e:
                logger.error(f"Unexpected error executing action {action.get('id')}: {e}")
                results.append(ExecutionResult(
                    success=False,
                    error=str(e),
                    duration=0.0,
                ))

        return results

    def execute_action(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
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
                self._create_backup(adapter, action_id)

            # Execute commands based on action type
            if action_type == "install":
                result = self._execute_install(adapter, action)
            elif action_type == "configure":
                result = self._execute_configure(adapter, action)
            elif action_type == "modify":
                result = self._execute_modify(adapter, action)
            elif action_type == "backup":
                result = self._execute_backup(adapter, action)
            elif action_type == "restore":
                result = self._execute_restore(adapter, action)
            elif action_type == "jailbreak":
                result = self._execute_jailbreak(adapter, action)
            elif action_type == "bypass":
                result = self._execute_bypass(adapter, action)
            else:
                # Generic command execution
                result = self._execute_commands(adapter, commands)

            duration = time.time() - start_time
            result.duration = duration

            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Action {action_id} failed: {e}")

            # Attempt rollback if available
            if "rollback_commands" in action:
                self._execute_rollback(adapter, action)

            return ExecutionResult(
                success=False,
                error=str(e),
                duration=duration,
            )

    def _execute_install(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
        """Execute install action."""
        package = action.get("package", "")
        if not package:
            return ExecutionResult(success=False, error="No package specified", duration=0.0)

        return adapter.install_package(package)

    def _execute_configure(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
        """Execute configure action."""
        # Configuration actions are typically file modifications
        file_path = action.get("file_path", "")
        changes = action.get("changes", {})

        if file_path and changes:
            return adapter.modify_file(file_path, changes)
        # Fall back to command execution
        commands = action.get("commands", [])
        return self._execute_commands(adapter, commands)

    def _execute_modify(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
        """Execute modify action."""
        file_path = action.get("file_path", "")
        changes = action.get("changes", {})

        if file_path and changes:
            return adapter.modify_file(file_path, changes)
        commands = action.get("commands", [])
        return self._execute_commands(adapter, commands)

    def _execute_backup(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
        """Execute backup action."""
        source = action.get("source", "")
        destination = action.get("destination", "")

        if source and destination:
            return adapter.create_backup(source, destination)
        return ExecutionResult(success=False, error="No source or destination specified", duration=0.0)

    def _execute_restore(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
        """Execute restore action."""
        backup_path = action.get("backup_path", "")
        destination = action.get("destination", "")

        if backup_path and destination:
            return adapter.restore_backup(backup_path, destination)
        return ExecutionResult(success=False, error="No backup path or destination specified", duration=0.0)

    def _execute_jailbreak(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
        """Execute jailbreak action (high risk)."""
        logger.warning("Executing jailbreak action - this is high risk!")
        commands = action.get("commands", [])
        return self._execute_commands(adapter, commands)

    def _execute_bypass(self, adapter: BaseAdapter, action: dict[str, Any]) -> ExecutionResult:
        """Execute bypass action (high risk)."""
        logger.warning("Executing bypass action - this is high risk!")
        commands = action.get("commands", [])
        return self._execute_commands(adapter, commands)

    def _execute_commands(self, adapter: BaseAdapter, commands: list[str]) -> ExecutionResult:
        """Execute a list of commands."""
        if not commands:
            return ExecutionResult(success=False, error="No commands specified", duration=0.0)

        # Execute commands sequentially
        for command in commands:
            result = adapter.execute_command(command)
            if not result.success:
                return result

        return ExecutionResult(success=True, duration=0.0)

    def _create_backup(self, adapter: BaseAdapter, action_id: str) -> None:
        """Create backup before high-risk operations."""
        # This would create a system backup
        logger.info(f"Creating backup for action {action_id}")
        # Implementation would depend on the specific backup strategy

    def _execute_rollback(self, adapter: BaseAdapter, action: dict[str, Any]) -> None:
        """Execute rollback commands."""
        rollback_commands = action.get("rollback_commands", [])

        if not rollback_commands:
            logger.warning("No rollback commands available")
            return

        logger.info(f"Executing rollback for action {action.get('id')}")

        for command in rollback_commands:
            try:
                result = adapter.execute_command(command)
                if not result.success:
                    logger.error(f"Rollback command failed: {command} - {result.error}")
            except Exception as e:
                logger.error(f"Rollback command failed: {command} - {e}")

    def get_supported_platforms(self) -> list[str]:
        """Get list of supported platforms."""
        return list(self.adapters.keys())

    def get_platform_capabilities(self, platform: str) -> list[str]:
        """Get capabilities for a specific platform."""
        try:
            adapter = self.get_adapter(platform)
            return adapter.get_capabilities()
        except ValueError:
            return []
