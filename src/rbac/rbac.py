"""Main RBAC class providing a high-level API.

This module provides the primary interface for using the RBAC system.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone

from .core.models import User, Permission, Resource, EntityStatus
from .core.models.role import Role, RoleAssignment
from .core.protocols import IStorageProvider, ICacheProvider
from .storage import MemoryStorage
from .engine import AuthorizationEngine, RoleHierarchyResolver
from .core.exceptions import RBACException


class RBAC:
    """Main RBAC interface.
    
    This class provides a simple, intuitive API for:
    - Managing users, roles, and permissions
    - Assigning roles to users
    - Checking permissions
    - Enforcing access control
    
    Example:
        >>> # Initialize with in-memory storage
        >>> rbac = RBAC(storage='memory')
        >>> 
        >>> # Create entities
        >>> user = rbac.create_user(
        ...     user_id="user_123",
        ...     email="alice@example.com",
        ...     name="Alice"
        ... )
        >>> 
        >>> role = rbac.create_role(
        ...     role_id="role_editor",
        ...     name="Editor",
        ...     permissions=["perm_doc_read", "perm_doc_write"]
        ... )
        >>> 
        >>> # Assign role
        >>> rbac.assign_role("user_123", "role_editor")
        >>> 
        >>> # Check permission
        >>> result = rbac.can("user_123", "read", "document")
        >>> if result:
        ...     # Grant access
        ...     pass
    """
    
    def __init__(
        self,
        storage: Union[str, IStorageProvider] = 'memory',
        cache: Optional[ICacheProvider] = None,
        enable_hierarchy: bool = True,
        enable_abac: bool = True
    ):
        """Initialize the RBAC system.
        
        Args:
            storage: Storage provider ('memory', 'sql', etc.) or provider instance
            cache: Optional cache provider for performance
            enable_hierarchy: Enable role hierarchy support
            enable_abac: Enable attribute-based access control
        """
        # Initialize storage
        if isinstance(storage, str):
            if storage == 'memory':
                self._storage = MemoryStorage()
            else:
                raise ValueError(f"Unknown storage type: {storage}")
        else:
            self._storage = storage
        
        self._cache = cache
        
        # Initialize authorization engine
        self._engine = AuthorizationEngine(
            storage=self._storage,
            cache=self._cache,
            enable_hierarchy=enable_hierarchy,
            enable_abac=enable_abac
        )
    
    # -------------------- High-Level API --------------------
    
    def can(
        self,
        user_id: str,
        action: str,
        resource: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if a user can perform an action on a resource.
        
        Simple convenience method that returns True/False.
        
        Args:
            user_id: ID of the user
            action: Action to perform (e.g., "read", "write", "delete")
            resource: Resource type string or dict with type and id
            context: Optional additional context for ABAC
            
        Returns:
            True if allowed, False otherwise
            
        Example:
            >>> rbac.can("user_123", "read", "document")
            True
            >>> rbac.can("user_123", "delete", {"type": "document", "id": "doc_456"})
            False
        """
        # Parse resource
        if isinstance(resource, str):
            resource_type = resource
            resource_id = None
        elif isinstance(resource, dict):
            resource_type = resource.get('type')
            resource_id = resource.get('id')
        else:
            raise ValueError("Resource must be a string or dict")
        
        # Check permission
        result = self._engine.check_permission(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            context=context
        )
        
        return result.allowed
    
    def check(
        self,
        user_id: str,
        action: str,
        resource: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Check permission and return detailed result.
        
        Args:
            user_id: ID of the user
            action: Action to perform
            resource: Resource type string or dict
            context: Optional additional context
            
        Returns:
            Dictionary with:
                - allowed: bool
                - reason: str
                - matched_permissions: List[str]
                - timestamp: datetime
        """
        # Parse resource
        if isinstance(resource, str):
            resource_type = resource
            resource_id = None
        elif isinstance(resource, dict):
            resource_type = resource.get('type')
            resource_id = resource.get('id')
        else:
            raise ValueError("Resource must be a string or dict")
        
        result = self._engine.check_permission(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            context=context
        )
        
        return {
            'allowed': result.allowed,
            'reason': result.reason,
            'matched_permissions': result.matched_permissions,
            'timestamp': result.timestamp.isoformat()
        }
    
    def require(
        self,
        user_id: str,
        action: str,
        resource: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Require permission, raising exception if denied.
        
        Args:
            user_id: ID of the user
            action: Action to perform
            resource: Resource type string or dict
            context: Optional additional context
            
        Raises:
            PermissionDenied: If user lacks permission
            
        Example:
            >>> rbac.require("user_123", "delete", "document")
            # Raises PermissionDenied if not allowed
        """
        from .core.exceptions import PermissionDenied
        
        result = self.check(user_id, action, resource, context)
        
        if not result['allowed']:
            raise PermissionDenied(
                f"User {user_id} cannot {action} on "
                f"{resource}: {result['reason']}"
            )
    
    # -------------------- User Management --------------------
    
    def create_user(
        self,
        user_id: str,
        email: str,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None
    ) -> User:
        """Create a new user.
        
        Args:
            user_id: Unique user ID (must start with "user_")
            email: User's email address
            name: User's display name
            attributes: Optional custom attributes
            domain: Optional domain/tenant
            
        Returns:
            Created User object
        """
        user = User(
            id=user_id,
            email=email,
            name=name,
            attributes=attributes or {},
            domain=domain,
            status=EntityStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return self._storage.create_user(user)
    
    def get_user(self, user_id: str) -> User:
        """Get a user by ID."""
        return self._storage.get_user(user_id)
    
    def list_users(
        self,
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[User]:
        """List users with optional filters."""
        return self._storage.list_users(domain, limit, offset)
    
    # -------------------- Role Management --------------------
    
    def create_role(
        self,
        role_id: str,
        name: str,
        permissions: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        domain: Optional[str] = None,
        description: Optional[str] = None
    ) -> Role:
        """Create a new role.
        
        Args:
            role_id: Unique role ID (must start with "role_")
            name: Role display name
            permissions: List of permission IDs
            parent_id: Optional parent role for inheritance
            domain: Optional domain/tenant
            description: Optional description
            
        Returns:
            Created Role object
        """
        role = Role(
            id=role_id,
            name=name,
            permissions=permissions or [],
            parent_id=parent_id,
            domain=domain,
            description=description,
            status=EntityStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return self._storage.create_role(role)
    
    def get_role(self, role_id: str) -> Role:
        """Get a role by ID."""
        return self._storage.get_role(role_id)
    
    def list_roles(
        self,
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Role]:
        """List roles with optional filters."""
        return self._storage.list_roles(domain, limit, offset)
    
    def add_permission_to_role(
        self,
        role_id: str,
        permission_id: str
    ) -> Role:
        """Add a permission to a role.
        
        Args:
            role_id: ID of the role
            permission_id: ID of the permission to add
            
        Returns:
            Updated Role object
        """
        role = self._storage.get_role(role_id)
        
        if permission_id not in role.permissions:
            # Create updated role (immutable)
            updated_role = Role(
                id=role.id,
                name=role.name,
                permissions=[*role.permissions, permission_id],
                parent_id=role.parent_id,
                domain=role.domain,
                description=role.description,
                status=role.status,
                created_at=role.created_at,
                updated_at=datetime.now(timezone.utc)
            )
            
            return self._storage.update_role(updated_role)
        
        return role
    
    # -------------------- Permission Management --------------------
    
    def create_permission(
        self,
        permission_id: str,
        resource_type: str,
        action: str,
        description: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> Permission:
        """Create a new permission.
        
        Args:
            permission_id: Unique permission ID (must start with "perm_")
            resource_type: Type of resource (e.g., "document", "user")
            action: Action allowed (e.g., "read", "write", "delete")
            description: Optional description
            conditions: Optional ABAC conditions
            
        Returns:
            Created Permission object
        """
        permission = Permission(
            id=permission_id,
            resource_type=resource_type,
            action=action,
            description=description,
            conditions=conditions
        )
        
        return self._storage.create_permission(permission)
    
    def get_permission(self, permission_id: str) -> Permission:
        """Get a permission by ID."""
        return self._storage.get_permission(permission_id)
    
    def list_permissions(
        self,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Permission]:
        """List permissions with optional filters."""
        return self._storage.list_permissions(resource_type, limit, offset)
    
    # -------------------- Role Assignment --------------------
    
    def assign_role(
        self,
        user_id: str,
        role_id: str,
        domain: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> RoleAssignment:
        """Assign a role to a user.
        
        Args:
            user_id: ID of the user
            role_id: ID of the role
            domain: Optional domain for scoped assignment
            granted_by: Optional ID of user who granted this role
            expires_at: Optional expiration time
            
        Returns:
            RoleAssignment object
        """
        assignment = RoleAssignment(
            user_id=user_id,
            role_id=role_id,
            domain=domain,
            granted_by=granted_by,
            granted_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        
        # Clear cache
        if self._cache:
            self._cache.delete(f"user_roles:{user_id}:{domain}")
        
        return self._storage.assign_role(assignment)
    
    def revoke_role(
        self,
        user_id: str,
        role_id: str,
        domain: Optional[str] = None
    ) -> bool:
        """Revoke a role from a user.
        
        Args:
            user_id: ID of the user
            role_id: ID of the role
            domain: Optional domain
            
        Returns:
            True if revoked, False if assignment didn't exist
        """
        # Clear cache
        if self._cache:
            self._cache.delete(f"user_roles:{user_id}:{domain}")
        
        return self._storage.revoke_role(user_id, role_id, domain)
    
    def get_user_roles(
        self,
        user_id: str,
        domain: Optional[str] = None
    ) -> List[Role]:
        """Get all roles assigned to a user."""
        return self._storage.get_user_roles(user_id, domain)
    
    def get_user_permissions(
        self,
        user_id: str,
        resource_type: Optional[str] = None
    ) -> List[Permission]:
        """Get all permissions available to a user.
        
        Includes permissions from all roles (direct and inherited).
        """
        return self._engine.get_user_permissions(user_id, resource_type)
    
    # -------------------- Resource Management --------------------
    
    def create_resource(
        self,
        resource_id: str,
        resource_type: str,
        attributes: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None
    ) -> Resource:
        """Create a new resource.
        
        Args:
            resource_id: Unique resource ID (must start with "resource_")
            resource_type: Type of resource (e.g., "document")
            attributes: Optional custom attributes
            domain: Optional domain/tenant
            
        Returns:
            Created Resource object
        """
        resource = Resource(
            id=resource_id,
            type=resource_type,
            attributes=attributes or {},
            domain=domain,
            status=EntityStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        return self._storage.create_resource(resource)
    
    def get_resource(self, resource_id: str) -> Resource:
        """Get a resource by ID."""
        return self._storage.get_resource(resource_id)
    
    # -------------------- Utility Methods --------------------
    
    @property
    def storage(self) -> IStorageProvider:
        """Get the storage provider."""
        return self._storage
    
    @property
    def engine(self) -> AuthorizationEngine:
        """Get the authorization engine."""
        return self._engine
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._engine.clear_cache()
