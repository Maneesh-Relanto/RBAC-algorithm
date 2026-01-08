"""
Core data models for RBAC framework.

This module defines the fundamental data structures used throughout
the RBAC system. All models are immutable by default for thread safety
and use dataclasses for clarity.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json


class EntityStatus(Enum):
    """Status of an entity in the system."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass(frozen=True)
class User:
    """
    Represents a user (subject/actor) in the RBAC system.
    
    A user is an entity that can be assigned roles and perform actions
    on resources. Users are immutable once created.
    
    Attributes:
        id: Unique identifier for the user
        email: User's email address (must be unique)
        name: Display name of the user
        attributes: Additional attributes for ABAC (department, location, etc.)
        status: Current status of the user account
        domain: Optional domain/tenant identifier
        created_at: Timestamp when user was created
        updated_at: Timestamp of last update
        
    Example:
        >>> user = User(
        ...     id="user_123",
        ...     email="john@example.com",
        ...     name="John Doe",
        ...     attributes={"department": "engineering", "level": "senior"}
        ... )
    """
    
    id: str
    email: str
    name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    status: EntityStatus = EntityStatus.ACTIVE
    domain: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate user data after initialization."""
        if not self.id:
            raise ValueError("User id cannot be empty")
        if not self.email or '@' not in self.email:
            raise ValueError("Valid email is required")
    
    def __hash__(self) -> int:
        """Make user hashable for use in sets and dicts."""
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        """Compare users by id."""
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def has_attribute(self, key: str, value: Any = None) -> bool:
        """
        Check if user has a specific attribute.
        
        Args:
            key: Attribute name
            value: Optional value to match (if None, just checks existence)
            
        Returns:
            True if attribute exists (and matches value if provided)
        """
        if key not in self.attributes:
            return False
        if value is None:
            return True
        return self.attributes[key] == value
    
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == EntityStatus.ACTIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "attributes": self.attributes,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create user from dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            New User instance
        """
        status = EntityStatus(data.get('status', 'active'))
        created_at = datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(timezone.utc)
        updated_at = datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now(timezone.utc)
        
        return cls(
            id=data['id'],
            email=data['email'],
            name=data.get('name'),
            attributes=data.get('attributes', {}),
            status=status,
            created_at=created_at,
            updated_at=updated_at
        )


# Alias for clarity in some contexts
Subject = User


@dataclass(frozen=True)
class Permission:
    """
    Represents a permission in the RBAC system.
    
    A permission defines a specific action that can be performed on a
    resource type. Permissions are the atomic units of authorization.
    
    Attributes:
        id: Unique identifier for the permission
        resource_type: Type of resource (e.g., "document", "api", "user")
        action: Action that can be performed (e.g., "read", "write", "delete")
        description: Human-readable description
        conditions: Optional conditions for the permission (for ABAC)
        
    Example:
        >>> perm = Permission(
        ...     id="perm_doc_read",
        ...     resource_type="document",
        ...     action="read",
        ...     description="Allows reading documents"
        ... )
    """
    
    id: str
    resource_type: str
    action: str
    description: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate permission data."""
        if not self.id:
            raise ValueError("Permission id cannot be empty")
        if not self.resource_type:
            raise ValueError("Resource type is required")
        if not self.action:
            raise ValueError("Action is required")
    
    def __hash__(self) -> int:
        """Make permission hashable."""
        return hash(self.id)
    
    def __eq__(self, other) -> bool:
        """Compare permissions by id."""
        if not isinstance(other, Permission):
            return False
        return self.id == other.id
    
    def matches(self, resource_type: str, action: str) -> bool:
        """
        Check if this permission matches given resource type and action.
        
        Args:
            resource_type: Resource type to match
            action: Action to match
            
        Returns:
            True if permission matches
        """
        # Support wildcards
        resource_match = (
            self.resource_type == "*" or 
            self.resource_type == resource_type
        )
        action_match = (
            self.action == "*" or 
            self.action == action
        )
        return resource_match and action_match
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert permission to dictionary."""
        return {
            "id": self.id,
            "resource_type": self.resource_type,
            "action": self.action,
            "description": self.description,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Permission':
        """Create permission from dictionary."""
        created_at = datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(timezone.utc)
        
        return cls(
            id=data['id'],
            resource_type=data['resource_type'],
            action=data['action'],
            description=data.get('description'),
            conditions=data.get('conditions', {}),
            created_at=created_at
        )


# Common action constants
class Action:
    """Standard CRUD actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    ADMIN = "admin"
    ALL = "*"


@dataclass(frozen=True)
class Resource:
    """
    Represents a resource in the RBAC system.
    
    A resource is any entity that access control applies to
    (documents, APIs, database records, etc.).
    
    Attributes:
        id: Unique identifier for the resource
        type: Type of resource (matches permission.resource_type)
        attributes: Additional attributes for ABAC (owner, status, etc.)
        parent_id: Optional parent resource for hierarchical resources
        domain: Optional domain/tenant for multi-tenancy
        status: Current status of the resource
        created_at: Timestamp when resource was created
        updated_at: Timestamp of last update
        
    Example:
        >>> resource = Resource(
        ...     id="doc_123",
        ...     type="document",
        ...     attributes={
        ...         "owner": "user_456",
        ...         "status": "published",
        ...         "department": "engineering"
        ...     },
        ...     domain="company_a"
        ... )
    """
    
    id: str
    type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    status: EntityStatus = EntityStatus.ACTIVE
    domain: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate resource data."""
        if not self.id:
            raise ValueError("Resource id cannot be empty")
        if not self.type:
            raise ValueError("Resource type is required")
    
    def __hash__(self) -> int:
        """Make resource hashable."""
        return hash((self.id, self.type))
    
    def __eq__(self, other) -> bool:
        """Compare resources by id and type."""
        if not isinstance(other, Resource):
            return False
        return self.id == other.id and self.type == other.type
    
    def has_attribute(self, key: str, value: Any = None) -> bool:
        """Check if resource has a specific attribute."""
        if key not in self.attributes:
            return False
        if value is None:
            return True
        return self.attributes[key] == value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "attributes": self.attributes,
            "parent_id": self.parent_id,
            "domain": self.domain,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Create resource from dictionary."""
        created_at = datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(timezone.utc)
        
        return cls(
            id=data['id'],
            type=data['type'],
            attributes=data.get('attributes', {}),
            parent_id=data.get('parent_id'),
            domain=data.get('domain'),
            created_at=created_at
        )
