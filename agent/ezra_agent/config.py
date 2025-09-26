"""Configuration management for Ezra agent."""

import hashlib
import json
import os
import platform
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Agent configuration model."""

    companion_url: str = Field(..., description="Companion server URL")
    device_id: str = Field(..., description="Unique device identifier")
    polling_interval: int = Field(
        default=5000, description="Polling interval in milliseconds",
    )
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=30000, description="Request timeout in milliseconds")
    log_level: str = Field(default="info", description="Logging level")
    data_dir: Path = Field(default=Path.home() / ".ezra", description="Data directory")
    cache_dir: Path = Field(
        default=Path.home() / ".ezra" / "cache", description="Cache directory",
    )
    backup_dir: Path = Field(
        default=Path.home() / ".ezra" / "backups", description="Backup directory",
    )


class ConfigManager:
    """Manages agent configuration."""

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration manager."""
        self.config_path = config_path or self._get_default_config_path()
        self._config: AgentConfig | None = None

    @property
    def config(self) -> AgentConfig:
        """Get current configuration."""
        return self._config or self.load()

    @config.setter
    def config(self, value: AgentConfig) -> None:
        """Set configuration."""
        self._config = value

    def _get_default_config_path(self) -> Path:
        """Get default configuration file path."""
        if os.name == "nt":  # Windows
            return Path(os.environ.get("APPDATA", "")) / "ezra" / "config.json"
        # Unix-like
        return Path.home() / ".ezra" / "config.json"

    def load(self) -> AgentConfig:
        """Load configuration from file."""
        if self._config is not None:
            return self._config

        if self.config_path.exists():
            try:
                with self.config_path.open(encoding="utf-8") as f:
                    config_data = json.load(f)
                self._config = AgentConfig(**config_data)
            except (json.JSONDecodeError, ValueError) as e:
                msg = f"Invalid configuration file: {e}"
                raise ValueError(msg) from e
        else:
            # Create default configuration
            self._config = self.create_default_config()
            self.save()

        return self._config

    def save(self) -> None:
        """Save configuration to file."""
        if self._config is None:
            msg = "No configuration loaded"
            raise ValueError(msg)

        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(self._config.dict(), f, indent=2, default=str)

    def create_default_config(self) -> AgentConfig:
        """Create default configuration."""
        return AgentConfig(
            companion_url=os.environ.get("EZRA_COMPANION_URL", "http://localhost:3000"),
            device_id=self._generate_device_id(),
        )

    def _generate_device_id(self) -> str:
        """Generate unique device ID."""
        # Create a unique identifier based on system information
        system_info = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

        # Hash the system info to create a stable device ID
        info_str = json.dumps(system_info, sort_keys=True)
        device_id = hashlib.sha256(info_str.encode()).hexdigest()[:16]

        return f"ezra_{device_id}"

    def update(self, **kwargs: Any) -> None:
        """Update configuration values."""
        if self._config is None:
            self.load()

        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        if self._config is None:
            self.load()

        return getattr(self._config, key, default)
