"""System adapters for different platforms."""

from .base import BaseAdapter
from .linux import LinuxAdapter
from .windows import WindowsAdapter
from .android import AndroidAdapter

__all__ = ['BaseAdapter', 'LinuxAdapter', 'WindowsAdapter', 'AndroidAdapter']
