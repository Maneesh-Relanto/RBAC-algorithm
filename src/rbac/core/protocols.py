"""
Abstract Protocols and Interfaces for RBAC System.

This module defines language-agnostic contracts that all implementations
must follow. Using Python's Protocol for structural typing.
"""

from typing import Protocol, Optional, List, Dict, Any, Set
from abc import abstractmethod
from datetime import datetime


class IUser(Protocol):
    """
    Interface for User entity.
    
    All language implementations should provide an equivalent structure.
    """
    id: str
    email: str
    name: Optional[str]
    attributes: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        ...
    
    def is_active(self) -> bool:
        """Check if user is active."""
        ...


class IRole(Protocol):
    """Interface for Role entity."""
    id: str
    name: str
    description: Optional[str]
    permissions: Set[str]
    parent_id: Optional[str]
    domain: Optional[str]
    status: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        ...
    
    def has_permission(self, permission_id: str) -> bool:
        """Check if role has permission."""
        ...


class IPermission(Protocol):
    """Interface for Permission entity."""
    id: str
    resource_type: str
    action: str
    description: Optional[str]
    conditions: Dict[str, Any]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        ...
    
    def matches(self, resource_type: str, action: str) -> bool:
        """Check if permission matches criteria."""
        ...


class IResource(Protocol):
    """Interface for Resource entity."""
    id: str
    type: str
    attributes: Dict[str, Any]
    parent_id: Optional[str]
    domain: Optional[str]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        ...


class IStorageProvider(Protocol):
    """
    Abstract Storage Provider Interface.
    
    All storage backends (SQL, NoSQL, in-memory) must implement this interface.
    This ensures interchangeability of storage solutions.
    """
    
    # User Operations
    @abstractmethod
    def create_user(self, user: IUser) -> IUser:
        """
        Create a new user.
        
        Args:
            user: User to create
            
        Returns:
            Created user with generated fields
            
        Raises:
            DataIntegrityError: If user already exists
        """
        ...
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[IUser]:
        """
        Retrieve user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User if found, None otherwise
        """
        ...
    
    @abstractmethod
    def update_user(self, user: IUser) -> IUser:
        """Update existing user."""
        ...
    
    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user.
        
        Args:
            user_id: User to delete
            
        Returns:
            True if deleted, False if not found
        """
        ...
    
    @abstractmethod
    def list_users(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[IUser]:
        """List users with optional filtering and pagination."""
        ...
    
    # Role Operations
    @abstractmethod
    def create_role(self, role: IRole) -> IRole:
        """Create a new role."""
        ...
    
    @abstractmethod
    def get_role(self, role_id: str) -> Optional[IRole]:
        """Retrieve role by ID."""
        ...
    
    @abstractmethod
    def update_role(self, role: IRole) -> IRole:
        """Update existing role."""
        ...
    
    @abstractmethod
    def delete_role(self, role_id: str) -> bool:
        """Delete role."""
        ...
    
    @abstractmethod
    def list_roles(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[IRole]:
        """List roles with optional filtering and pagination."""
        ...
    
    # Permission Operations
    @abstractmethod
    def create_permission(self, permission: IPermission) -> IPermission:
        """Create a new permission."""
        ...
    
    @abstractmethod
    def get_permission(self, permission_id: str) -> Optional[IPermission]:
        """Retrieve permission by ID."""
        ...
    
    @abstractmethod
    def delete_permission(self, permission_id: str) -> bool:
        """Delete permission."""
        ...
    
    @abstractmethod
    def list_permissions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[IPermission]:
        """List permissions with optional filtering."""
        ...
    
    # Assignment Operations
    @abstractmethod
    def assign_role(
        self,
        user_id: str,
        role_id: str,
        domain: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assign role to user."""
        ...
    
    @abstractmethod
    def revoke_role(
        self,
        user_id: str,
        role_id: str,
        domain: Optional[str] = None
    ) -> bool:
        """Revoke role from user."""
        ...
    
    @abstractmethod
    def get_user_roles(
        self,
        user_id: str,
        domain: Optional[str] = None,
        include_expired: bool = False
    ) -> List[IRole]:
        """Get all roles assigned to a user."""
        ...
    
    @abstractmethod
    def get_role_users(self, role_id: str) -> List[IUser]:
        """Get all users with a specific role."""
        ...


class ICacheProvider(Protocol):
    """
    Abstract Cache Provider Interface.
    
    Implementations can use Redis, Memcached, or in-memory caching.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        ...
    
    @abstractmethod
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache with optional TTL in seconds."""
        ...
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove value from cache."""
        ...
    
    @abstractmethod
    def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching pattern. Returns count cleared."""
        ...
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...


class IAuditLogger(Protocol):
    """
    Abstract Audit Logger Interface.
    
    All authorization decisions should be logged for compliance and debugging.
    """
    
    @abstractmethod
    def log_authorization(
        self,
        user_id: str,
        action: str,
        resource: Dict[str, Any],
        decision: bool,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an authorization decision."""
        ...
    
    @abstractmethod
    def log_role_assignment(
        self,
        user_id: str,
        role_id: str,
        granted_by: str,
        action: str  # 'assigned' or 'revoked'
    ) -> None:
        """Log role assignment changes."""
        ...
    
    @abstractmethod
    def log_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log errors."""
        ...


class IAuthorizationEngine(Protocol):
    """
    Abstract Authorization Engine Interface.
    
    Core engine that evaluates authorization requests.
    """
    
    @abstractmethod
    def check_permission(
        self,
        user_id: str,
        action: str,
        resource: IResource,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if user has permission to perform action on resource.
        
        Args:
            user_id: User identifier
            action: Action to perform
            resource: Resource being accessed
            context: Additional context (domain, IP, etc.)
            
        Returns:
            Dictionary with keys:
            - allowed (bool): Authorization decision
            - reason (str): Explanation
            - matched_permissions (list): Permissions that granted access
            - evaluation_time_ms (float): Processing time
        """
        ...
    
    @abstractmethod
    def batch_check(
        self,
        checks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Perform multiple authorization checks efficiently.
        
        Args:
            checks: List of check requests
            
        Returns:
            List of authorization results in same order
        """
        ...
    
    @abstractmethod
    def get_user_permissions(
        self,
        user_id: str,
        resource_type: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[IPermission]:
        """Get all permissions for a user (including inherited)."""
        ...
    
    @abstractmethod
    def get_allowed_actions(
        self,
        user_id: str,
        resource: IResource
    ) -> List[str]:
        """Get all actions user can perform on a resource."""
        ...


class IRoleHierarchyResolver(Protocol):
    """
    Abstract Role Hierarchy Resolver.
    
    Handles role inheritance and hierarchy traversal.
    """
    
    @abstractmethod
    def get_inherited_permissions(
        self,
        role: IRole
    ) -> Set[str]:
        """
        Get all permissions including inherited from parent roles.
        
        Args:
            role: Starting role
            
        Returns:
            Set of all permission IDs (direct + inherited)
        """
        ...
    
    @abstractmethod
    def get_role_chain(
        self,
        role_id: str
    ) -> List[IRole]:
        """
        Get complete role inheritance chain.
        
        Args:
            role_id: Starting role
            
        Returns:
            List of roles from leaf to root
        """
        ...
    
    @abstractmethod
    def validate_hierarchy(
        self,
        role_id: str,
        parent_id: str
    ) -> bool:
        """
        Validate that adding parent doesn't create circular dependency.
        
        Returns:
            True if valid, False if creates cycle
        """
        ...
    
    @abstractmethod
    def get_hierarchy_depth(self, role_id: str) -> int:
        """Get depth of role in hierarchy (0 = root)."""
        ...


class IPolicyEvaluator(Protocol):
    """
    Abstract Policy Evaluator for ABAC conditions.
    
    Evaluates attribute-based conditions on permissions.
    """
    
    @abstractmethod
    def evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        user: IUser,
        resource: IResource,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate ABAC conditions.
        
        Args:
            conditions: Conditions to evaluate
            user: User attempting access
            resource: Resource being accessed
            context: Additional context
            
        Returns:
            True if all conditions pass
        """
        ...
