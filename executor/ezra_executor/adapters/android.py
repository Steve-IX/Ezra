"""Android system adapter."""

import os
import shutil
import subprocess
import time
from typing import Any

from .base import BaseAdapter, ExecutionResult, SystemInfo


class AndroidAdapter(BaseAdapter):
    """Android system adapter."""

    def __init__(self):
        """Initialize Android adapter."""
        super().__init__()

    def get_platform(self) -> str:
        """Get the platform name."""
        return "android"

    def get_system_info(self) -> SystemInfo:
        """Get system information."""
        # Android system info is limited without root
        return SystemInfo(
            platform="android",
            version="Android (version detection limited)",
            architecture="arm64",  # Most modern Android devices
            capabilities=self._capabilities,
        )

    def execute_command(self, command: str, timeout: int = 300) -> ExecutionResult:
        """Execute a system command."""
        start_time = time.time()

        try:
            # Android commands are limited without root
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
        """Install a package (APK)."""
        # Android package installation is limited without root
        if package.endswith(".apk"):
            command = f"adb install {package}"
        else:
            # Try to install from Google Play (limited)
            command = f'am start -a android.intent.action.VIEW -d "market://details?id={package}"'

        return self.execute_command(command)

    def uninstall_package(self, package: str, **kwargs) -> ExecutionResult:
        """Uninstall a package."""
        command = f"adb uninstall {package}"
        return self.execute_command(command)

    def list_packages(self) -> list[str]:
        """List installed packages."""
        result = self.execute_command("pm list packages")
        if result.success:
            packages = []
            for line in result.output.split("\n"):
                if line.startswith("package:"):
                    packages.append(line.replace("package:", ""))
            return packages
        return []

    def get_package_info(self, package: str) -> dict[str, Any] | None:
        """Get information about a package."""
        result = self.execute_command(f"dumpsys package {package}")
        if result.success:
            return {
                "name": package,
                "installed": True,
                "info": result.output,
            }
        return None

    def create_backup(self, source: str, destination: str) -> ExecutionResult:
        """Create a backup (limited on Android)."""
        # Android backup is limited without root
        command = f'cp -r "{source}" "{destination}"'
        return self.execute_command(command)

    def restore_backup(self, backup_path: str, destination: str) -> ExecutionResult:
        """Restore from a backup."""
        command = f'cp -r "{backup_path}" "{destination}"'
        return self.execute_command(command)

    def modify_file(self, file_path: str, changes: dict[str, Any]) -> ExecutionResult:
        """Modify a file (limited on Android)."""
        if "content" in changes:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(changes["content"])
                return ExecutionResult(success=True, duration=0.0)
            except Exception as e:
                return ExecutionResult(success=False, error=str(e), duration=0.0)

        return ExecutionResult(success=False, error="No valid changes specified", duration=0.0)

    def get_file_info(self, file_path: str) -> dict[str, Any] | None:
        """Get file information."""
        try:
            stat_info = os.stat(file_path)
            return {
                "path": file_path,
                "size": stat_info.st_size,
                "permissions": oct(stat_info.st_mode)[-3:],
                "owner": stat_info.st_uid,
                "group": stat_info.st_gid,
                "modified": stat_info.st_mtime,
                "exists": True,
            }
        except (OSError, FileNotFoundError):
            return None

    def set_permissions(self, file_path: str, permissions: str) -> ExecutionResult:
        """Set file permissions."""
        try:
            # Convert permissions string to octal
            if isinstance(permissions, str):
                if permissions.startswith("0"):
                    perm_octal = int(permissions, 8)
                else:
                    perm_octal = int(permissions, 8)
            else:
                perm_octal = permissions

            os.chmod(file_path, perm_octal)
            return ExecutionResult(success=True, duration=0.0)

        except Exception as e:
            return ExecutionResult(success=False, error=str(e), duration=0.0)

    def get_permissions(self, file_path: str) -> str | None:
        """Get file permissions."""
        try:
            stat_info = os.stat(file_path)
            return oct(stat_info.st_mode)[-3:]
        except (OSError, FileNotFoundError):
            return None

    def _detect_capabilities(self) -> None:
        """Detect Android system capabilities."""
        # Basic capabilities
        self._add_capability("file_system")
        self._add_capability("process_management")
        self._add_capability("network")

        # Check for ADB
        if shutil.which("adb"):
            self._add_capability("adb_access")

        # Check for root access
        try:
            result = self.execute_command('su -c "id"')
            if result.success and "uid=0" in result.output:
                self._add_capability("root_access")
        except:
            pass

        # Check for development tools
        if shutil.which("git"):
            self._add_capability("git")
        if shutil.which("python"):
            self._add_capability("python")
        if shutil.which("node"):
            self._add_capability("nodejs")

        # Check for package managers
        if shutil.which("apt"):
            self._add_capability("apt_package_manager")
        if shutil.which("pkg"):
            self._add_capability("pkg_package_manager")
