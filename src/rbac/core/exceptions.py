"""
Custom exceptions for RBAC operations.

This module defines all exceptions used throughout the RBAC framework,
following a hierarchical structure for granular error handling.

Exception Hierarchy:
    RBACException (base)
    ├── AuthorizationError
    │   ├── PermissionDenied
    │   └── AccessDenied
    ├── ResourceError
    │   ├── UserNotFound
    │   ├── RoleNotFound
    │   ├── PermissionNotFound
    │   └── ResourceNotFound
    ├── ValidationError
    │   ├── InvalidInput
    │   └── InvalidConfiguration
    └── StorageError
        ├── ConnectionError
        └── DataIntegrityError
"""

from typing import Optional, Any


class RBACException(Exception):
    """
    Base exception for all RBAC-related errors.
    
    All custom exceptions in the RBAC framework inherit from this class,
    allowing for broad exception catching when needed.
    
    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional context about the error
    """
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """
        Initialize RBACException.
        
        Args:
            message: Error description
            code: Optional error code for programmatic handling
            details: Optional additional context
        """
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        base = f"[{self.code}] {self.message}"
        if self.details:
            base += f" | Details: {self.details}"
        return base


# Authorization Errors
class AuthorizationError(RBACException):
    """Base class for authorization-related errors."""
    pass


class PermissionDenied(AuthorizationError):
    """
    Raised when a user lacks required permissions.
    
    This exception indicates that the user's identity is verified,
    but they don't have the necessary permissions for the requested action.
    
    Example:
        >>> if not has_permission(user, "delete", resource):
        ...     raise PermissionDenied(
        ...         f"User {user.id} cannot delete {resource.id}",
        ...         details={"user_id": user.id, "resource_id": resource.id}
        ...     )
    """
    
    def __init__(self, message: str = "Permission denied", **kwargs):
        super().__init__(message, code="PERMISSION_DENIED", **kwargs)


class AccessDenied(AuthorizationError):
    """
    Raised when access to a resource is denied.
    
    Similar to PermissionDenied but more general, can be used for
    policy-level or context-based denials.
    """
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, code="ACCESS_DENIED", **kwargs)


# Resource Errors
class ResourceError(RBACException):
    """Base class for resource-related errors."""
    pass


class UserNotFound(ResourceError):
    """
    Raised when a requested user does not exist.
    
    Example:
        >>> user = storage.get_user(user_id)
        >>> if user is None:
        ...     raise UserNotFound(f"User {user_id} not found")
    """
    
    def __init__(self, message: str, user_id: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if user_id:
            details['user_id'] = user_id
        super().__init__(message, code="USER_NOT_FOUND", details=details)


class RoleNotFound(ResourceError):
    """
    Raised when a requested role does not exist.
    
    Example:
        >>> role = storage.get_role(role_id)
        >>> if role is None:
        ...     raise RoleNotFound(f"Role {role_id} not found")
    """
    
    def __init__(self, message: str, role_id: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if role_id:
            details['role_id'] = role_id
        super().__init__(message, code="ROLE_NOT_FOUND", details=details)


class PermissionNotFound(ResourceError):
    """Raised when a requested permission does not exist."""
    
    def __init__(self, message: str, permission_id: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if permission_id:
            details['permission_id'] = permission_id
        super().__init__(message, code="PERMISSION_NOT_FOUND", details=details)


class ResourceNotFound(ResourceError):
    """Raised when a requested resource does not exist."""
    
    def __init__(self, message: str, resource_id: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if resource_id:
            details['resource_id'] = resource_id
        super().__init__(message, code="RESOURCE_NOT_FOUND", details=details)


# Validation Errors
class ValidationError(RBACException):
    """Base class for validation-related errors."""
    pass


class InvalidInput(ValidationError):
    """
    Raised when input validation fails.
    
    Example:
        >>> if not email_pattern.match(email):
        ...     raise InvalidInput(
        ...         "Invalid email format",
        ...         details={"email": email, "field": "email"}
        ...     )
    """
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if field:
            details['field'] = field
        super().__init__(message, code="INVALID_INPUT", details=details)


class InvalidConfiguration(ValidationError):
    """
    Raised when configuration is invalid.
    
    Example:
        >>> if max_depth < 1:
        ...     raise InvalidConfiguration(
        ...         "max_depth must be at least 1",
        ...         details={"max_depth": max_depth}
        ...     )
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="INVALID_CONFIGURATION", **kwargs)


# Storage Errors
class StorageError(RBACException):
    """Base class for storage-related errors."""
    pass


class ConnectionError(StorageError):
    """
    Raised when storage connection fails.
    
    Example:
        >>> try:
        ...     connection = storage.connect()
        ... except Exception as e:
        ...     raise ConnectionError(
        ...         f"Failed to connect to storage: {e}",
        ...         details={"storage_type": "postgresql"}
        ...     )
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="CONNECTION_ERROR", **kwargs)


class DataIntegrityError(StorageError):
    """
    Raised when data integrity is violated.
    
    Example:
        >>> if duplicate_role:
        ...     raise DataIntegrityError(
        ...         f"Role {role_id} already exists",
        ...         details={"role_id": role_id}
        ...     )
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="DATA_INTEGRITY_ERROR", **kwargs)


# Hierarchy Errors
class HierarchyError(RBACException):
    """Base class for role hierarchy errors."""
    pass


class CircularDependency(HierarchyError):
    """
    Raised when a circular dependency is detected in role hierarchy.
    
    Example:
        >>> if creates_cycle(role, new_parent):
        ...     raise CircularDependency(
        ...         f"Adding {new_parent} as parent creates circular dependency",
        ...         details={"role": role.id, "parent": new_parent.id}
        ...     )
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="CIRCULAR_DEPENDENCY", **kwargs)


class MaxDepthExceeded(HierarchyError):
    """
    Raised when role hierarchy exceeds maximum depth.
    
    Example:
        >>> if depth > MAX_DEPTH:
        ...     raise MaxDepthExceeded(
        ...         f"Role hierarchy depth {depth} exceeds maximum {MAX_DEPTH}",
        ...         details={"current_depth": depth, "max_depth": MAX_DEPTH}
        ...     )
    """
    
    def __init__(self, message: str, current_depth: int, max_depth: int, **kwargs):
        details = kwargs.get('details', {})
        details.update({"current_depth": current_depth, "max_depth": max_depth})
        super().__init__(message, code="MAX_DEPTH_EXCEEDED", details=details)


# Policy Errors
class PolicyError(RBACException):
    """Base class for policy-related errors."""
    pass


class PolicyNotFound(PolicyError):
    """Raised when a requested policy does not exist."""
    
    def __init__(self, message: str, policy_id: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if policy_id:
            details['policy_id'] = policy_id
        super().__init__(message, code="POLICY_NOT_FOUND", details=details)


class PolicyEvaluationError(PolicyError):
    """
    Raised when policy evaluation fails.
    
    Example:
        >>> try:
        ...     result = evaluate_policy(policy, context)
        ... except Exception as e:
        ...     raise PolicyEvaluationError(
        ...         f"Failed to evaluate policy: {e}",
        ...         details={"policy_id": policy.id}
        ...     )
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="POLICY_EVALUATION_ERROR", **kwargs)


# Cache Errors
class CacheError(RBACException):
    """Base class for cache-related errors."""
    pass


class CacheConnectionError(CacheError):
    """Raised when cache connection fails."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="CACHE_CONNECTION_ERROR", **kwargs)


class CacheInvalidationError(CacheError):
    """Raised when cache invalidation fails."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, code="CACHE_INVALIDATION_ERROR", **kwargs)
