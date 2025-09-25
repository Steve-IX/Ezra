"""Linux system adapter."""

import os
import subprocess
import shutil
import stat
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from .base import BaseAdapter, ExecutionResult, SystemInfo


class LinuxAdapter(BaseAdapter):
    """Linux system adapter."""
    
    def __init__(self):
        """Initialize Linux adapter."""
        super().__init__()
    
    def get_platform(self) -> str:
        """Get the platform name."""
        return "linux"
    
    def get_system_info(self) -> SystemInfo:
        """Get system information."""
        import platform
        import psutil
        
        # Get distribution info
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = {}
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
            
            version = f"{os_info.get('NAME', 'Linux')} {os_info.get('VERSION', '')}"
        except FileNotFoundError:
            version = f"Linux {platform.release()}"
        
        return SystemInfo(
            platform="linux",
            version=version,
            architecture=platform.machine(),
            capabilities=self._capabilities,
        )
    
    def execute_command(self, command: str, timeout: int = 300) -> ExecutionResult:
        """Execute a system command."""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
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
        
        if package_manager == 'apt':
            return self._install_with_apt(package)
        elif package_manager == 'yum':
            return self._install_with_yum(package)
        elif package_manager == 'dnf':
            return self._install_with_dnf(package)
        elif package_manager == 'pacman':
            return self._install_with_pacman(package)
        elif package_manager == 'snap':
            return self._install_with_snap(package)
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
        
        if package_manager == 'apt':
            return self._uninstall_with_apt(package)
        elif package_manager == 'yum':
            return self._uninstall_with_yum(package)
        elif package_manager == 'dnf':
            return self._uninstall_with_dnf(package)
        elif package_manager == 'pacman':
            return self._uninstall_with_pacman(package)
        elif package_manager == 'snap':
            return self._uninstall_with_snap(package)
        else:
            return ExecutionResult(
                success=False,
                error=f"Unsupported package manager: {package_manager}",
                duration=0.0,
            )
    
    def list_packages(self) -> List[str]:
        """List installed packages."""
        package_manager = self._detect_package_manager()
        
        if package_manager == 'apt':
            result = self.execute_command('dpkg -l | grep "^ii" | awk "{print $2}"')
        elif package_manager == 'yum':
            result = self.execute_command('yum list installed | awk "{print $1}"')
        elif package_manager == 'dnf':
            result = self.execute_command('dnf list installed | awk "{print $1}"')
        elif package_manager == 'pacman':
            result = self.execute_command('pacman -Q | awk "{print $1}"')
        else:
            return []
        
        if result.success:
            return [pkg.strip() for pkg in result.output.split('\n') if pkg.strip()]
        else:
            return []
    
    def get_package_info(self, package: str) -> Optional[Dict[str, Any]]:
        """Get information about a package."""
        package_manager = self._detect_package_manager()
        
        if package_manager == 'apt':
            result = self.execute_command(f'dpkg -s {package}')
        elif package_manager == 'yum':
            result = self.execute_command(f'yum info {package}')
        elif package_manager == 'dnf':
            result = self.execute_command(f'dnf info {package}')
        elif package_manager == 'pacman':
            result = self.execute_command(f'pacman -Qi {package}')
        else:
            return None
        
        if result.success:
            # Parse package info (simplified)
            return {
                'name': package,
                'installed': True,
                'info': result.output,
            }
        else:
            return None
    
    def create_backup(self, source: str, destination: str) -> ExecutionResult:
        """Create a backup using tar."""
        # Ensure destination directory exists
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create tar backup
        command = f'tar -czf "{destination}" -C "{Path(source).parent}" "{Path(source).name}"'
        return self.execute_command(command)
    
    def restore_backup(self, backup_path: str, destination: str) -> ExecutionResult:
        """Restore from a tar backup."""
        # Ensure destination directory exists
        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Extract tar backup
        command = f'tar -xzf "{backup_path}" -C "{destination}"'
        return self.execute_command(command)
    
    def modify_file(self, file_path: str, changes: Dict[str, Any]) -> ExecutionResult:
        """Modify a file."""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated file modification
        
        if 'content' in changes:
            # Replace entire file content
            try:
                with open(file_path, 'w') as f:
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
        """Set file permissions."""
        try:
            # Convert permissions string to octal
            if isinstance(permissions, str):
                if permissions.startswith('0'):
                    perm_octal = int(permissions, 8)
                else:
                    perm_octal = int(permissions, 8)
            else:
                perm_octal = permissions
            
            os.chmod(file_path, perm_octal)
            return ExecutionResult(success=True, duration=0.0)
            
        except Exception as e:
            return ExecutionResult(success=False, error=str(e), duration=0.0)
    
    def get_permissions(self, file_path: str) -> Optional[str]:
        """Get file permissions."""
        try:
            stat_info = os.stat(file_path)
            return oct(stat_info.st_mode)[-3:]
        except (OSError, FileNotFoundError):
            return None
    
    def _detect_capabilities(self) -> None:
        """Detect Linux system capabilities."""
        # Basic capabilities
        self._add_capability('file_system')
        self._add_capability('process_management')
        self._add_capability('network')
        
        # Check for package managers
        if shutil.which('apt'):
            self._add_capability('apt_package_manager')
        if shutil.which('yum'):
            self._add_capability('yum_package_manager')
        if shutil.which('dnf'):
            self._add_capability('dnf_package_manager')
        if shutil.which('pacman'):
            self._add_capability('pacman_package_manager')
        if shutil.which('snap'):
            self._add_capability('snap_package_manager')
        
        # Check for systemd
        if Path('/etc/systemd').exists():
            self._add_capability('systemd')
        
        # Check for root access
        if os.geteuid() == 0:
            self._add_capability('root_access')
        
        # Check for development tools
        if shutil.which('git'):
            self._add_capability('git')
        if shutil.which('docker'):
            self._add_capability('docker')
        if shutil.which('python3'):
            self._add_capability('python')
        if shutil.which('node'):
            self._add_capability('nodejs')
        
        # Check for virtualization
        if shutil.which('kvm'):
            self._add_capability('kvm_virtualization')
        if shutil.which('virtualbox'):
            self._add_capability('virtualbox')
    
    def _detect_package_manager(self) -> str:
        """Detect the primary package manager."""
        if shutil.which('apt'):
            return 'apt'
        elif shutil.which('dnf'):
            return 'dnf'
        elif shutil.which('yum'):
            return 'yum'
        elif shutil.which('pacman'):
            return 'pacman'
        elif shutil.which('snap'):
            return 'snap'
        else:
            return 'unknown'
    
    def _install_with_apt(self, package: str) -> ExecutionResult:
        """Install package with apt."""
        command = f'sudo apt update && sudo apt install -y {package}'
        return self.execute_command(command)
    
    def _install_with_yum(self, package: str) -> ExecutionResult:
        """Install package with yum."""
        command = f'sudo yum install -y {package}'
        return self.execute_command(command)
    
    def _install_with_dnf(self, package: str) -> ExecutionResult:
        """Install package with dnf."""
        command = f'sudo dnf install -y {package}'
        return self.execute_command(command)
    
    def _install_with_pacman(self, package: str) -> ExecutionResult:
        """Install package with pacman."""
        command = f'sudo pacman -S --noconfirm {package}'
        return self.execute_command(command)
    
    def _install_with_snap(self, package: str) -> ExecutionResult:
        """Install package with snap."""
        command = f'sudo snap install {package}'
        return self.execute_command(command)
    
    def _uninstall_with_apt(self, package: str) -> ExecutionResult:
        """Uninstall package with apt."""
        command = f'sudo apt remove -y {package}'
        return self.execute_command(command)
    
    def _uninstall_with_yum(self, package: str) -> ExecutionResult:
        """Uninstall package with yum."""
        command = f'sudo yum remove -y {package}'
        return self.execute_command(command)
    
    def _uninstall_with_dnf(self, package: str) -> ExecutionResult:
        """Uninstall package with dnf."""
        command = f'sudo dnf remove -y {package}'
        return self.execute_command(command)
    
    def _uninstall_with_pacman(self, package: str) -> ExecutionResult:
        """Uninstall package with pacman."""
        command = f'sudo pacman -R --noconfirm {package}'
        return self.execute_command(command)
    
    def _uninstall_with_snap(self, package: str) -> ExecutionResult:
        """Uninstall package with snap."""
        command = f'sudo snap remove {package}'
        return self.execute_command(command)
