"""
RBAC Algorithm - Enterprise-Grade Authorization Framework

This package provides a production-ready Role-Based Access Control (RBAC)
implementation with excellent developer experience and enterprise reliability.

License:
    MIT License - see LICENSE file for details
"""

__version__ = "0.1.0"
__author__ = "RBAC Algorithm Contributors"
__license__ = "MIT"

from .rbac import RBAC
from .core.models import User, Permission, Resource, EntityStatus
from .core.models.role import Role, RoleAssignment
from .core.exceptions import (
    RBACException,
    PermissionDenied,
    UserNotFound,
    RoleNotFound,
    PermissionNotFound,
    ResourceNotFound,
    DuplicateEntityError,
    ValidationError,
    CircularDependencyError,
    StorageError,
    PolicyEvaluationError,
    AuthorizationError
)
from .matrix import PermissionsMatrixManager, PermissionsMatrix, MatrixMode

__all__ = [
    # Version
    "__version__",
    
    # Main class
    "RBAC",
    
    # Models
    "User",
    "Role",
    "Permission",
    "Resource",
    "RoleAssignment",
    "EntityStatus",
    
    # Matrix
    "PermissionsMatrixManager",
    "PermissionsMatrix",
    "MatrixMode",
    
    # Exceptions
    "RBACException",
    "PermissionDenied",
    "UserNotFound",
    "RoleNotFound",
    "PermissionNotFound",
    "ResourceNotFound",
    "DuplicateEntityError",
    "ValidationError",
    "CircularDependencyError",
    "StorageError",
    "PolicyEvaluationError",
    "AuthorizationError",
]
