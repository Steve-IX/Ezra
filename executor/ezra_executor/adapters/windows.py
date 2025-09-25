"""Windows system adapter."""

import os
import subprocess
import shutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from .base import BaseAdapter, ExecutionResult, SystemInfo


class WindowsAdapter(BaseAdapter):
    """Windows system adapter."""
    
    def __init__(self):
        """Initialize Windows adapter."""
        super().__init__()
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return "windows"
    
    def get_system_info(self) -> SystemInfo:
        """Get system information."""
        import platform
        
        return SystemInfo(
            platform="windows",
            version=f"Windows {platform.release()} {platform.version()}",
            architecture=platform.machine(),
            capabilities=self._capabilities,
        )
    
    def execute_command(self, command: str, timeout: int = 300) -> ExecutionResult:
        """Execute a system command."""
        start_time = time.time()
        
        try:
            # Use PowerShell for better Windows compatibility
            if command.startswith('powershell') or command.startswith('pwsh'):
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            else:
                # Wrap in PowerShell for better error handling
                ps_command = f'powershell -Command "& {{{command}}}"'
                result = subprocess.run(
                    ps_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            
            duration = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                exit_code=result.returncode,
                duration=duration,
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                error=f"Command timed out after {timeout} seconds",
                duration=duration,
            )
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                error=str(e),
                duration=duration,
            )
    
    def install_package(self, package: str, **kwargs) -> ExecutionResult:
        """Install a package using the appropriate package manager."""
        package_manager = kwargs.get('package_manager', 'auto')
        
        if package_manager == 'auto':
            package_manager = self._detect_package_manager()
        
        if package_manager == 'choco':
            return self._install_with_choco(package)
        elif package_manager == 'winget':
            return self._install_with_winget(package)
        elif package_manager == 'scoop':
            return self._install_with_scoop(package)
        else:
            return ExecutionResult(
                success=False,
                error=f"Unsupported package manager: {package_manager}",
                duration=0.0,
            )
    
    def uninstall_package(self, package: str, **kwargs) -> ExecutionResult:
        """Uninstall a package."""
        package_manager = kwargs.get('package_manager', 'auto')
        
        if package_manager == 'auto':
            package_manager = self._detect_package_manager()
        
        if package_manager == 'choco':
            return self._uninstall_with_choco(package)
        elif package_manager == 'winget':
            return self._uninstall_with_winget(package)
        elif package_manager == 'scoop':
            return self._uninstall_with_scoop(package)
        else:
            return ExecutionResult(
                success=False,
                error=f"Unsupported package manager: {package_manager}",
                duration=0.0,
            )
    
    def list_packages(self) -> List[str]:
        """List installed packages."""
        package_manager = self._detect_package_manager()
        
        if package_manager == 'choco':
            result = self.execute_command('choco list --local-only')
        elif package_manager == 'winget':
            result = self.execute_command('winget list')
        elif package_manager == 'scoop':
            result = self.execute_command('scoop list')
        else:
            return []
        
        if result.success:
            # Parse package list (simplified)
            lines = result.output.split('\n')
            packages = []
            for line in lines:
                if line.strip() and not line.startswith('Name'):
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
            return packages
        else:
            return []
    
    def get_package_info(self, package: str) -> Optional[Dict[str, Any]]:
        """Get information about a package."""
        package_manager = self._detect_package_manager()
        
        if package_manager == 'choco':
            result = self.execute_command(f'choco info {package}')
        elif package_manager == 'winget':
            result = self.execute_command(f'winget show {package}')
        elif package_manager == 'scoop':
            result = self.execute_command(f'scoop info {package}')
        else:
            return None
        
        if result.success:
            return {
                'name': package,
                'installed': True,
                'info': result.output,
            }
        else:
            return None
    
    def create_backup(self, source: str, destination: str) -> ExecutionResult:
        """Create a backup using robocopy or xcopy."""
        # Ensure destination directory exists
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use robocopy for better Windows compatibility
        command = f'robocopy "{source}" "{destination}" /E /COPYALL'
        return self.execute_command(command)
    
    def restore_backup(self, backup_path: str, destination: str) -> ExecutionResult:
        """Restore from a backup."""
        # Ensure destination directory exists
        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Use robocopy to restore
        command = f'robocopy "{backup_path}" "{destination}" /E /COPYALL'
        return self.execute_command(command)
    
    def modify_file(self, file_path: str, changes: Dict[str, Any]) -> ExecutionResult:
        """Modify a file."""
        if 'content' in changes:
            # Replace entire file content
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(changes['content'])
                return ExecutionResult(success=True, duration=0.0)
            except Exception as e:
                return ExecutionResult(success=False, error=str(e), duration=0.0)
        
        return ExecutionResult(success=False, error="No valid changes specified", duration=0.0)
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information."""
        try:
            stat_info = os.stat(file_path)
            return {
                'path': file_path,
                'size': stat_info.st_size,
                'permissions': oct(stat_info.st_mode)[-3:],
                'owner': stat_info.st_uid,
                'group': stat_info.st_gid,
                'modified': stat_info.st_mtime,
                'exists': True,
            }
        except (OSError, FileNotFoundError):
            return None
    
    def set_permissions(self, file_path: str, permissions: str) -> ExecutionResult:
        """Set file permissions using icacls."""
        try:
            # Use icacls for Windows permissions
            command = f'icacls "{file_path}" /grant Everyone:F'
            return self.execute_command(command)
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), duration=0.0)
    
    def get_permissions(self, file_path: str) -> Optional[str]:
        """Get file permissions using icacls."""
        try:
            result = self.execute_command(f'icacls "{file_path}"')
            if result.success:
                return result.output
            else:
                return None
        except Exception:
            return None
    
    def _detect_capabilities(self) -> None:
        """Detect Windows system capabilities."""
        # Basic capabilities
        self._add_capability('file_system')
        self._add_capability('process_management')
        self._add_capability('network')
        self._add_capability('powershell')
        self._add_capability('registry_access')
        
        # Check for package managers
        if shutil.which('choco'):
            self._add_capability('chocolatey_package_manager')
        if shutil.which('winget'):
            self._add_capability('winget_package_manager')
        if shutil.which('scoop'):
            self._add_capability('scoop_package_manager')
        
        # Check for Windows services
        if Path('C:\\Windows\\System32\\services.exe').exists():
            self._add_capability('windows_services')
        
        # Check for administrator access
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                self._add_capability('administrator_access')
        except:
            pass
        
        # Check for development tools
        if shutil.which('git'):
            self._add_capability('git')
        if shutil.which('docker'):
            self._add_capability('docker')
        if shutil.which('python'):
            self._add_capability('python')
        if shutil.which('node'):
            self._add_capability('nodejs')
        
        # Check for virtualization
        if shutil.which('virtualbox'):
            self._add_capability('virtualbox')
        if shutil.which('hyper-v'):
            self._add_capability('hyper_v')
    
    def _detect_package_manager(self) -> str:
        """Detect the primary package manager."""
        if shutil.which('choco'):
            return 'choco'
        elif shutil.which('winget'):
            return 'winget'
        elif shutil.which('scoop'):
            return 'scoop'
        else:
            return 'unknown'
    
    def _install_with_choco(self, package: str) -> ExecutionResult:
        """Install package with Chocolatey."""
        command = f'choco install {package} -y'
        return self.execute_command(command)
    
    def _install_with_winget(self, package: str) -> ExecutionResult:
        """Install package with winget."""
        command = f'winget install {package}'
        return self.execute_command(command)
    
    def _install_with_scoop(self, package: str) -> ExecutionResult:
        """Install package with Scoop."""
        command = f'scoop install {package}'
        return self.execute_command(command)
    
    def _uninstall_with_choco(self, package: str) -> ExecutionResult:
        """Uninstall package with Chocolatey."""
        command = f'choco uninstall {package} -y'
        return self.execute_command(command)
    
    def _uninstall_with_winget(self, package: str) -> ExecutionResult:
        """Uninstall package with winget."""
        command = f'winget uninstall {package}'
        return self.execute_command(command)
    
    def _uninstall_with_scoop(self, package: str) -> ExecutionResult:
        """Uninstall package with Scoop."""
        command = f'scoop uninstall {package}'
        return self.execute_command(command)
