"""System adapters for different platforms."""

from .android import AndroidAdapter
from .base import BaseAdapter
from .linux import LinuxAdapter
from .windows import WindowsAdapter

__all__ = ["AndroidAdapter", "BaseAdapter", "LinuxAdapter", "WindowsAdapter"]
