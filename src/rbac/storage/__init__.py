"""Storage providers for RBAC system.

This module contains storage provider implementations that follow the
IStorageProvider protocol defined in core.protocols.

Available backends:
    - :class:`MemoryStorage`      – in-process dict storage (dev/test)
    - :class:`SQLAlchemyStorage`  – SQL-backed storage (SQLite, PostgreSQL, MySQL)
"""

from .base import BaseStorage
from .memory import MemoryStorage

try:
    from .sqlalchemy_adapter import SQLAlchemyStorage
    _SQLALCHEMY_AVAILABLE = True
except ImportError:
    _SQLALCHEMY_AVAILABLE = False

__all__ = ['BaseStorage', 'MemoryStorage', 'SQLAlchemyStorage']
