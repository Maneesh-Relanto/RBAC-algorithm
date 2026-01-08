"""Storage providers for RBAC system.

This module contains storage provider implementations that follow the
IStorageProvider protocol defined in core.protocols.
"""

from .base import BaseStorage
from .memory import MemoryStorage

__all__ = ['BaseStorage', 'MemoryStorage']
