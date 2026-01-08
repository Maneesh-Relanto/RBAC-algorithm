"""In-memory storage provider for RBAC system.

This implementation stores all data in memory using dictionaries.
Suitable for development, testing, and small-scale deployments.

Thread Safety: This implementation uses basic dictionaries and is NOT
thread-safe. For production use, consider using threading.Lock or
a thread-safe storage backend.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import copy

from .base import BaseStorage
from ..core.models import User, Permission, Resource, EntityStatus
from ..core.models.role import Role, RoleAssignment
from ..core.exceptions import (
    UserNotFound, RoleNotFound, PermissionNotFound, 
    ResourceNotFound, DuplicateEntityError, StorageError
)


class MemoryStorage(BaseStorage):
    """In-memory storage implementation using dictionaries.
    
    This storage provider keeps all data in memory. Data is lost when
    the application restarts. Use for development and testing only.
    
    Example:
        >>> storage = MemoryStorage()
        >>> user = User(id="user_1", email="test@example.com", name="Test User")
        >>> storage.create_user(user)
        >>> retrieved = storage.get_user("user_1")
    """
    
    def __init__(self):
        """Initialize empty storage."""
        # Main entity stores
        self._users: Dict[str, User] = {}
        self._roles: Dict[str, Role] = {}
        self._permissions: Dict[str, Permission] = {}
        self._resources: Dict[str, Resource] = {}
        self._role_assignments: List[RoleAssignment] = []
        
        # Indexes for faster lookups
        self._user_roles: Dict[str, List[str]] = defaultdict(list)  # user_id -> [role_ids]
        self._role_users: Dict[str, List[str]] = defaultdict(list)  # role_id -> [user_ids]
        self._role_children: Dict[str, List[str]] = defaultdict(list)  # role_id -> [child_role_ids]
        
        # Domain indexes
        self._users_by_domain: Dict[Optional[str], List[str]] = defaultdict(list)
        self._roles_by_domain: Dict[Optional[str], List[str]] = defaultdict(list)
    
    # -------------------- User Operations --------------------
    
    def create_user(self, user: User) -> User:
        """Create a new user."""
        self._validate_user(user)
        
        if user.id in self._users:
            raise DuplicateEntityError(f"User {user.id} already exists")
        
        # Deep copy to prevent external modifications
        stored_user = copy.deepcopy(user)
        self._users[stored_user.id] = stored_user
        self._users_by_domain[stored_user.domain].append(stored_user.id)
        
        return copy.deepcopy(stored_user)
    
    def get_user(self, user_id: str) -> User:
        """Retrieve a user by ID."""
        if user_id not in self._users:
            raise UserNotFound(f"User {user_id} not found")
        
        user = self._users[user_id]
        if user.status == EntityStatus.DELETED:
            raise UserNotFound(f"User {user_id} not found")
        
        return copy.deepcopy(user)
    
    def update_user(self, user: User) -> User:
        """Update an existing user."""
        self._validate_user(user)
        
        if user.id not in self._users:
            raise UserNotFound(f"User {user.id} not found")
        
        old_user = self._users[user.id]
        
        # Update domain index if domain changed
        if old_user.domain != user.domain:
            self._users_by_domain[old_user.domain].remove(user.id)
            self._users_by_domain[user.domain].append(user.id)
        
        # Update timestamps
        updated_user = copy.deepcopy(user)
        updated_user.updated_at = datetime.utcnow()
        
        self._users[user.id] = updated_user
        return copy.deepcopy(updated_user)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user (soft delete by marking as DELETED)."""
        if user_id not in self._users:
            raise UserNotFound(f"User {user_id} not found")
        
        user = self._users[user_id]
        user.status = EntityStatus.DELETED
        user.updated_at = datetime.utcnow()
        
        # Remove all role assignments
        self._role_assignments = [
            ra for ra in self._role_assignments 
            if ra.user_id != user_id
        ]
        self._user_roles[user_id] = []
        
        return True
    
    def list_users(
        self, 
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[User]:
        """List users with optional domain filter."""
        if domain is not None:
            user_ids = self._users_by_domain.get(domain, [])
            users = [self._users[uid] for uid in user_ids]
        else:
            users = list(self._users.values())
        
        # Filter out deleted users
        users = [u for u in users if u.status != EntityStatus.DELETED]
        
        # Apply pagination
        return [copy.deepcopy(u) for u in users[offset:offset + limit]]
    
    # -------------------- Role Operations --------------------
    
    def create_role(self, role: Role) -> Role:
        """Create a new role."""
        self._validate_role(role)
        
        if role.id in self._roles:
            raise DuplicateEntityError(f"Role {role.id} already exists")
        
        # Validate parent exists
        if role.parent_id:
            if role.parent_id not in self._roles:
                raise RoleNotFound(f"Parent role {role.parent_id} not found")
            
            # Check for circular dependency
            self._check_circular_hierarchy(
                role.id, 
                role.parent_id,
                lambda rid: self._roles.get(rid)
            )
        
        stored_role = copy.deepcopy(role)
        self._roles[stored_role.id] = stored_role
        self._roles_by_domain[stored_role.domain].append(stored_role.id)
        
        # Update hierarchy index
        if stored_role.parent_id:
            self._role_children[stored_role.parent_id].append(stored_role.id)
        
        return copy.deepcopy(stored_role)
    
    def get_role(self, role_id: str) -> Role:
        """Retrieve a role by ID."""
        if role_id not in self._roles:
            raise RoleNotFound(f"Role {role_id} not found")
        
        role = self._roles[role_id]
        if role.status == EntityStatus.DELETED:
            raise RoleNotFound(f"Role {role_id} not found")
        
        return copy.deepcopy(role)
    
    def update_role(self, role: Role) -> Role:
        """Update an existing role."""
        self._validate_role(role)
        
        if role.id not in self._roles:
            raise RoleNotFound(f"Role {role.id} not found")
        
        old_role = self._roles[role.id]
        
        # Update domain index if changed
        if old_role.domain != role.domain:
            self._roles_by_domain[old_role.domain].remove(role.id)
            self._roles_by_domain[role.domain].append(role.id)
        
        # Update hierarchy index if parent changed
        if old_role.parent_id != role.parent_id:
            if old_role.parent_id:
                self._role_children[old_role.parent_id].remove(role.id)
            if role.parent_id:
                # Check for circular dependency
                self._check_circular_hierarchy(
                    role.id,
                    role.parent_id,
                    lambda rid: self._roles.get(rid)
                )
                self._role_children[role.parent_id].append(role.id)
        
        updated_role = copy.deepcopy(role)
        updated_role.updated_at = datetime.utcnow()
        
        self._roles[role.id] = updated_role
        return copy.deepcopy(updated_role)
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role (soft delete)."""
        if role_id not in self._roles:
            raise RoleNotFound(f"Role {role_id} not found")
        
        role = self._roles[role_id]
        
        # Check if role has children
        if self._role_children[role_id]:
            raise StorageError(
                f"Cannot delete role {role_id}: it has child roles"
            )
        
        role.status = EntityStatus.DELETED
        role.updated_at = datetime.utcnow()
        
        # Remove all assignments
        self._role_assignments = [
            ra for ra in self._role_assignments 
            if ra.role_id != role_id
        ]
        self._role_users[role_id] = []
        
        return True
    
    def list_roles(
        self, 
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Role]:
        """List roles with optional domain filter."""
        if domain is not None:
            role_ids = self._roles_by_domain.get(domain, [])
            roles = [self._roles[rid] for rid in role_ids]
        else:
            roles = list(self._roles.values())
        
        # Filter out deleted roles
        roles = [r for r in roles if r.status != EntityStatus.DELETED]
        
        # Apply pagination
        return [copy.deepcopy(r) for r in roles[offset:offset + limit]]
    
    # -------------------- Permission Operations --------------------
    
    def create_permission(self, permission: Permission) -> Permission:
        """Create a new permission."""
        self._validate_permission(permission)
        
        if permission.id in self._permissions:
            raise DuplicateEntityError(
                f"Permission {permission.id} already exists"
            )
        
        stored_perm = copy.deepcopy(permission)
        self._permissions[stored_perm.id] = stored_perm
        
        return copy.deepcopy(stored_perm)
    
    def get_permission(self, permission_id: str) -> Permission:
        """Retrieve a permission by ID."""
        if permission_id not in self._permissions:
            raise PermissionNotFound(
                f"Permission {permission_id} not found"
            )
        
        return copy.deepcopy(self._permissions[permission_id])
    
    def list_permissions(
        self,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Permission]:
        """List permissions with optional resource type filter."""
        permissions = list(self._permissions.values())
        
        if resource_type:
            permissions = [
                p for p in permissions 
                if p.resource_type == resource_type
            ]
        
        # Apply pagination
        return [copy.deepcopy(p) for p in permissions[offset:offset + limit]]
    
    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission."""
        if permission_id not in self._permissions:
            raise PermissionNotFound(
                f"Permission {permission_id} not found"
            )
        
        # Remove from all roles
        for role in self._roles.values():
            if permission_id in role.permissions:
                role.permissions.remove(permission_id)
        
        del self._permissions[permission_id]
        return True
    
    # -------------------- Resource Operations --------------------
    
    def create_resource(self, resource: Resource) -> Resource:
        """Create a new resource."""
        self._validate_resource(resource)
        
        if resource.id in self._resources:
            raise DuplicateEntityError(
                f"Resource {resource.id} already exists"
            )
        
        stored_resource = copy.deepcopy(resource)
        self._resources[stored_resource.id] = stored_resource
        
        return copy.deepcopy(stored_resource)
    
    def get_resource(self, resource_id: str) -> Resource:
        """Retrieve a resource by ID."""
        if resource_id not in self._resources:
            raise ResourceNotFound(f"Resource {resource_id} not found")
        
        resource = self._resources[resource_id]
        if resource.status == EntityStatus.DELETED:
            raise ResourceNotFound(f"Resource {resource_id} not found")
        
        return copy.deepcopy(resource)
    
    def list_resources(
        self,
        resource_type: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Resource]:
        """List resources with optional filters."""
        resources = list(self._resources.values())
        
        # Apply filters
        if resource_type:
            resources = [r for r in resources if r.type == resource_type]
        
        if domain is not None:
            resources = [r for r in resources if r.domain == domain]
        
        # Filter out deleted
        resources = [r for r in resources if r.status != EntityStatus.DELETED]
        
        # Apply pagination
        return [copy.deepcopy(r) for r in resources[offset:offset + limit]]
    
    def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource (soft delete)."""
        if resource_id not in self._resources:
            raise ResourceNotFound(f"Resource {resource_id} not found")
        
        resource = self._resources[resource_id]
        resource.status = EntityStatus.DELETED
        resource.updated_at = datetime.utcnow()
        
        return True
    
    # -------------------- Role Assignment Operations --------------------
    
    def assign_role(self, assignment: RoleAssignment) -> RoleAssignment:
        """Assign a role to a user."""
        self._validate_role_assignment(assignment)
        
        # Verify user and role exist
        if assignment.user_id not in self._users:
            raise UserNotFound(f"User {assignment.user_id} not found")
        
        if assignment.role_id not in self._roles:
            raise RoleNotFound(f"Role {assignment.role_id} not found")
        
        # Check if assignment already exists
        for existing in self._role_assignments:
            if (existing.user_id == assignment.user_id and 
                existing.role_id == assignment.role_id and
                existing.domain == assignment.domain):
                raise DuplicateEntityError(
                    f"User {assignment.user_id} already has role "
                    f"{assignment.role_id} in domain {assignment.domain}"
                )
        
        stored_assignment = copy.deepcopy(assignment)
        self._role_assignments.append(stored_assignment)
        
        # Update indexes
        self._user_roles[assignment.user_id].append(assignment.role_id)
        self._role_users[assignment.role_id].append(assignment.user_id)
        
        return copy.deepcopy(stored_assignment)
    
    def revoke_role(
        self, 
        user_id: str, 
        role_id: str,
        domain: Optional[str] = None
    ) -> bool:
        """Revoke a role from a user."""
        initial_count = len(self._role_assignments)
        
        self._role_assignments = [
            ra for ra in self._role_assignments
            if not (ra.user_id == user_id and 
                   ra.role_id == role_id and
                   ra.domain == domain)
        ]
        
        if len(self._role_assignments) == initial_count:
            return False  # No assignment found
        
        # Update indexes
        if role_id in self._user_roles[user_id]:
            self._user_roles[user_id].remove(role_id)
        if user_id in self._role_users[role_id]:
            self._role_users[role_id].remove(user_id)
        
        return True
    
    def get_user_roles(
        self, 
        user_id: str,
        domain: Optional[str] = None
    ) -> List[Role]:
        """Get all roles assigned to a user."""
        if user_id not in self._users:
            raise UserNotFound(f"User {user_id} not found")
        
        now = datetime.utcnow()
        role_ids = set()
        
        for assignment in self._role_assignments:
            if assignment.user_id != user_id:
                continue
            
            if domain is not None and assignment.domain != domain:
                continue
            
            # Skip expired assignments
            if assignment.expires_at and assignment.expires_at < now:
                continue
            
            role_ids.add(assignment.role_id)
        
        # Return role objects
        roles = []
        for role_id in role_ids:
            try:
                role = self.get_role(role_id)
                roles.append(role)
            except RoleNotFound:
                continue
        
        return roles
    
    def get_role_users(
        self, 
        role_id: str,
        domain: Optional[str] = None
    ) -> List[User]:
        """Get all users with a specific role."""
        if role_id not in self._roles:
            raise RoleNotFound(f"Role {role_id} not found")
        
        now = datetime.utcnow()
        user_ids = set()
        
        for assignment in self._role_assignments:
            if assignment.role_id != role_id:
                continue
            
            if domain is not None and assignment.domain != domain:
                continue
            
            # Skip expired assignments
            if assignment.expires_at and assignment.expires_at < now:
                continue
            
            user_ids.add(assignment.user_id)
        
        # Return user objects
        users = []
        for user_id in user_ids:
            try:
                user = self.get_user(user_id)
                users.append(user)
            except UserNotFound:
                continue
        
        return users
    
    # -------------------- Utility Methods --------------------
    
    def clear_all(self) -> None:
        """Clear all data (for testing)."""
        self._users.clear()
        self._roles.clear()
        self._permissions.clear()
        self._resources.clear()
        self._role_assignments.clear()
        self._user_roles.clear()
        self._role_users.clear()
        self._role_children.clear()
        self._users_by_domain.clear()
        self._roles_by_domain.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get storage statistics."""
        return {
            'users': len([u for u in self._users.values() 
                         if u.status != EntityStatus.DELETED]),
            'roles': len([r for r in self._roles.values() 
                         if r.status != EntityStatus.DELETED]),
            'permissions': len(self._permissions),
            'resources': len([r for r in self._resources.values() 
                             if r.status != EntityStatus.DELETED]),
            'role_assignments': len(self._role_assignments),
        }
