"""Base adapter for system operations."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """Execution result model."""
    
    success: bool = Field(..., description="Whether the operation succeeded")
    output: str = Field(default="", description="Command output")
    error: Optional[str] = Field(None, description="Error message")
    exit_code: int = Field(default=0, description="Exit code")
    duration: float = Field(..., description="Execution duration in seconds")


class SystemInfo(BaseModel):
    """System information model."""
    
    platform: str = Field(..., description="Platform name")
    version: str = Field(..., description="Platform version")
    architecture: str = Field(..., description="System architecture")
    capabilities: List[str] = Field(default_factory=list, description="System capabilities")


class BaseAdapter(ABC):
    """Base class for system adapters."""
    
    def __init__(self):
        """Initialize the adapter."""
        self._capabilities: List[str] = []
        self._detect_capabilities()
    
    @abstractmethod
    def get_platform(self) -> str:
        """Get the platform name."""
        pass
    
    @abstractmethod
    def get_system_info(self) -> SystemInfo:
        """Get system information."""
        pass
    
    @abstractmethod
    def execute_command(self, command: str, timeout: int = 300) -> ExecutionResult:
        """Execute a system command."""
        pass
    
    @abstractmethod
    def install_package(self, package: str, **kwargs) -> ExecutionResult:
        """Install a package."""
        pass
    
    @abstractmethod
    def uninstall_package(self, package: str, **kwargs) -> ExecutionResult:
        """Uninstall a package."""
        pass
    
    @abstractmethod
    def list_packages(self) -> List[str]:
        """List installed packages."""
        pass
    
    @abstractmethod
    def get_package_info(self, package: str) -> Optional[Dict[str, Any]]:
        """Get information about a package."""
        pass
    
    @abstractmethod
    def create_backup(self, source: str, destination: str) -> ExecutionResult:
        """Create a backup of files or directories."""
        pass
    
    @abstractmethod
    def restore_backup(self, backup_path: str, destination: str) -> ExecutionResult:
        """Restore from a backup."""
        pass
    
    @abstractmethod
    def modify_file(self, file_path: str, changes: Dict[str, Any]) -> ExecutionResult:
        """Modify a file."""
        pass
    
    @abstractmethod
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information."""
        pass
    
    @abstractmethod
    def set_permissions(self, file_path: str, permissions: str) -> ExecutionResult:
        """Set file permissions."""
        pass
    
    @abstractmethod
    def get_permissions(self, file_path: str) -> Optional[str]:
        """Get file permissions."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get system capabilities."""
        return self._capabilities.copy()
    
    def has_capability(self, capability: str) -> bool:
        """Check if system has a specific capability."""
        return capability in self._capabilities
    
    @abstractmethod
    def _detect_capabilities(self) -> None:
        """Detect system capabilities."""
        pass
    
    def _add_capability(self, capability: str) -> None:
        """Add a capability to the list."""
        if capability not in self._capabilities:
            self._capabilities.append(capability)
    
    def _remove_capability(self, capability: str) -> None:
        """Remove a capability from the list."""
        if capability in self._capabilities:
            self._capabilities.remove(capability)
