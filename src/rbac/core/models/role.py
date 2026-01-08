"""
Role model for RBAC system.

This module defines the Role data structure and related functionality
for managing roles and role hierarchies.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime

from rbac.core.models import Permission, EntityStatus


@dataclass(frozen=True)
class Role:
    """
    Represents a role in the RBAC system.
    
    A role is a named collection of permissions that can be assigned to users.
    Roles support hierarchical relationships through parent roles, enabling
    permission inheritance.
    
    Attributes:
        id: Unique identifier for the role
        name: Human-readable name for the role
        description: Optional description of the role's purpose
        permissions: Set of permissions directly assigned to this role
        parent_id: Optional parent role ID for inheritance
        domain: Optional domain/tenant for multi-tenancy
        status: Current status of the role
        metadata: Additional metadata about the role
        created_at: Timestamp when role was created
        updated_at: Timestamp of last update
        
    Example:
        >>> admin_role = Role(
        ...     id="role_admin",
        ...     name="Administrator",
        ...     description="Full system access",
        ...     permissions={read_perm, write_perm, delete_perm}
        ... )
        >>> editor_role = Role(
        ...     id="role_editor",
        ...     name="Editor",
        ...     description="Can edit content",
        ...     permissions={read_perm, write_perm},
        ...     parent_id="role_admin"  # Inherits from admin
        ... )
    """
    
    id: str
    name: str
    description: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)  # Permission IDs
    parent_id: Optional[str] = None
    domain: Optional[str] = None
    status: EntityStatus = EntityStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate role data after initialization."""
        if not self.id:
            raise ValueError("Role id cannot be empty")
        if not self.name:
            raise ValueError("Role name cannot be empty")
        
        # Ensure permissions is a set
        if not isinstance(self.permissions, set):
            object.__setattr__(self, 'permissions', set(self.permissions))
    
    def __hash__(self) -> int:
        """Make role hashable for use in sets and dicts."""
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        """Compare roles by id."""
        if not isinstance(other, Role):
            return False
        return self.id == other.id
    
    def has_permission(self, permission_id: str) -> bool:
        """
        Check if role has a specific permission.
        
        Args:
            permission_id: ID of the permission to check
            
        Returns:
            True if role has the permission
            
        Note:
            This only checks direct permissions, not inherited ones.
            Use RoleManager to check inherited permissions.
        """
        return permission_id in self.permissions
    
    def is_active(self) -> bool:
        """Check if role is active."""
        return self.status == EntityStatus.ACTIVE
    
    def has_parent(self) -> bool:
        """Check if role has a parent."""
        return self.parent_id is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert role to dictionary representation.
        
        Returns:
            Dictionary containing all role data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": list(self.permissions),
            "parent_id": self.parent_id,
            "domain": self.domain,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """
        Create role from dictionary.
        
        Args:
            data: Dictionary containing role data
            
        Returns:
            New Role instance
            
        Example:
            >>> role_data = {
            ...     "id": "role_admin",
            ...     "name": "Administrator",
            ...     "permissions": ["perm_1", "perm_2"]
            ... }
            >>> role = Role.from_dict(role_data)
        """
        status = EntityStatus(data.get('status', 'active'))
        created_at = (
            datetime.fromisoformat(data['created_at']) 
            if 'created_at' in data 
            else datetime.utcnow()
        )
        updated_at = (
            datetime.fromisoformat(data['updated_at']) 
            if 'updated_at' in data 
            else datetime.utcnow()
        )
        
        # Convert permissions list to set
        permissions = set(data.get('permissions', []))
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            permissions=permissions,
            parent_id=data.get('parent_id'),
            domain=data.get('domain'),
            status=status,
            metadata=data.get('metadata', {}),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def with_permissions(self, permissions: Set[str]) -> 'Role':
        """
        Create a new role with updated permissions.
        
        Since roles are immutable, this creates a new instance.
        
        Args:
            permissions: New set of permission IDs
            
        Returns:
            New Role instance with updated permissions
        """
        return Role(
            id=self.id,
            name=self.name,
            description=self.description,
            permissions=permissions,
            parent_id=self.parent_id,
            domain=self.domain,
            status=self.status,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )
    
    def with_parent(self, parent_id: Optional[str]) -> 'Role':
        """
        Create a new role with updated parent.
        
        Args:
            parent_id: New parent role ID or None
            
        Returns:
            New Role instance with updated parent
        """
        return Role(
            id=self.id,
            name=self.name,
            description=self.description,
            permissions=self.permissions,
            parent_id=parent_id,
            domain=self.domain,
            status=self.status,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )


@dataclass(frozen=True)
class RoleAssignment:
    """
    Represents the assignment of a role to a user.
    
    This is an association entity that tracks which users have which roles,
    potentially with additional context like domain or expiration.
    
    Attributes:
        user_id: ID of the user
        role_id: ID of the role
        domain: Optional domain for multi-tenancy
        granted_by: Optional ID of user who granted this role
        granted_at: Timestamp when role was granted
        expires_at: Optional expiration timestamp
        metadata: Additional context about the assignment
        
    Example:
        >>> assignment = RoleAssignment(
        ...     user_id="user_123",
        ...     role_id="role_admin",
        ...     domain="company_a",
        ...     granted_by="user_456",
        ...     expires_at=datetime(2026, 12, 31)
        ... )
    """
    
    user_id: str
    role_id: str
    domain: Optional[str] = None
    granted_by: Optional[str] = None
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate role assignment data."""
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.role_id:
            raise ValueError("Role ID cannot be empty")
    
    def is_expired(self) -> bool:
        """
        Check if role assignment has expired.
        
        Returns:
            True if expired, False otherwise
        """
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def is_active(self) -> bool:
        """Check if role assignment is currently active."""
        return not self.is_expired()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role assignment to dictionary."""
        return {
            "user_id": self.user_id,
            "role_id": self.role_id,
            "domain": self.domain,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoleAssignment':
        """Create role assignment from dictionary."""
        granted_at = (
            datetime.fromisoformat(data['granted_at']) 
            if 'granted_at' in data 
            else datetime.utcnow()
        )
        expires_at = (
            datetime.fromisoformat(data['expires_at']) 
            if data.get('expires_at') 
            else None
        )
        
        return cls(
            user_id=data['user_id'],
            role_id=data['role_id'],
            domain=data.get('domain'),
            granted_by=data.get('granted_by'),
            granted_at=granted_at,
            expires_at=expires_at,
            metadata=data.get('metadata', {})
        )
