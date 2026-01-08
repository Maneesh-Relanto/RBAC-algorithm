"""Base storage provider implementation with common utilities."""

from abc import ABC
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.protocols import IStorageProvider
from ..core.models import User, Permission, Resource
from ..core.models.role import Role, RoleAssignment
from ..core.exceptions import (
    ValidationError, UserNotFound, RoleNotFound, 
    PermissionNotFound, ResourceNotFound
)


class BaseStorage(IStorageProvider, ABC):
    """Base class for storage providers with common validation logic."""
    
    def _validate_user(self, user: User) -> None:
        """Validate user data."""
        if not user.id or not user.id.startswith('user_'):
            raise ValidationError("User ID must start with 'user_'")
        
        if not user.email or '@' not in user.email:
            raise ValidationError("Valid email is required")
        
        if not user.name or len(user.name.strip()) == 0:
            raise ValidationError("User name cannot be empty")
    
    def _validate_role(self, role: Role) -> None:
        """Validate role data."""
        if not role.id or not role.id.startswith('role_'):
            raise ValidationError("Role ID must start with 'role_'")
        
        if not role.name or len(role.name.strip()) == 0:
            raise ValidationError("Role name cannot be empty")
        
        # Validate permissions exist
        if role.permissions:
            for perm_id in role.permissions:
                if not perm_id.startswith('perm_'):
                    raise ValidationError(
                        f"Invalid permission ID format: {perm_id}"
                    )
    
    def _validate_permission(self, permission: Permission) -> None:
        """Validate permission data."""
        if not permission.id or not permission.id.startswith('perm_'):
            raise ValidationError("Permission ID must start with 'perm_'")
        
        if not permission.resource_type:
            raise ValidationError("Resource type is required")
        
        if not permission.action:
            raise ValidationError("Action is required")
    
    def _validate_resource(self, resource: Resource) -> None:
        """Validate resource data."""
        if not resource.id or not resource.id.startswith('resource_'):
            raise ValidationError("Resource ID must start with 'resource_'")
        
        if not resource.type:
            raise ValidationError("Resource type is required")
    
    def _validate_role_assignment(self, assignment: RoleAssignment) -> None:
        """Validate role assignment data."""
        if not assignment.user_id or not assignment.user_id.startswith('user_'):
            raise ValidationError("Valid user ID is required")
        
        if not assignment.role_id or not assignment.role_id.startswith('role_'):
            raise ValidationError("Valid role ID is required")
        
        # Check if assignment is expired
        if assignment.expires_at and assignment.expires_at < datetime.utcnow():
            raise ValidationError("Role assignment has expired")
    
    def _check_circular_hierarchy(
        self, 
        role_id: str, 
        parent_id: Optional[str],
        get_role_func
    ) -> None:
        """Check for circular dependencies in role hierarchy.
        
        Args:
            role_id: The role being updated
            parent_id: The proposed parent role
            get_role_func: Function to retrieve a role by ID
            
        Raises:
            CircularDependencyError: If setting parent_id would create a cycle
        """
        if not parent_id:
            return
        
        # Can't be parent of itself
        if role_id == parent_id:
            from ..core.exceptions import CircularDependencyError
            raise CircularDependencyError(
                f"Role {role_id} cannot be its own parent"
            )
        
        # Check if any ancestor is the current role
        current = parent_id
        visited = set()
        
        while current:
            if current in visited:
                from ..core.exceptions import CircularDependencyError
                raise CircularDependencyError(
                    f"Circular dependency detected in role hierarchy"
                )
            
            visited.add(current)
            
            if current == role_id:
                from ..core.exceptions import CircularDependencyError
                raise CircularDependencyError(
                    f"Role {role_id} is already an ancestor of {parent_id}"
                )
            
            try:
                parent_role = get_role_func(current)
                current = parent_role.parent_id if parent_role else None
            except RoleNotFound:
                break
    
    def _is_valid_filter(self, filters: Optional[Dict[str, Any]]) -> bool:
        """Validate filter dictionary."""
        if filters is None:
            return True
        
        if not isinstance(filters, dict):
            return False
        
        # Check for SQL injection attempts (basic check)
        dangerous_patterns = [';', '--', '/*', '*/', 'DROP', 'DELETE', 'UPDATE']
        for key, value in filters.items():
            if isinstance(value, str):
                value_upper = value.upper()
                if any(pattern in value_upper for pattern in dangerous_patterns):
                    return False
        
        return True
