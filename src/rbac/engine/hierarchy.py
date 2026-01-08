"""Role hierarchy resolver.

Handles role inheritance and hierarchy resolution to determine
all effective roles for a user.
"""

from typing import List, Set, Optional, Dict, Any
from dataclasses import dataclass

from ..core.protocols import IRoleHierarchyResolver, IStorageProvider
from ..core.models.role import Role
from ..core.exceptions import CircularDependencyError, RoleNotFound


@dataclass
class RoleHierarchy:
    """Represents the resolved hierarchy for a role."""
    role_id: str
    ancestors: List[str]  # Parent, grandparent, etc. (bottom to top)
    descendants: List[str]  # Children, grandchildren, etc. (top to bottom)
    depth: int  # Distance from root (roles with no parent)


class RoleHierarchyResolver(IRoleHierarchyResolver):
    """Resolves role hierarchies and inheritance.
    
    This class handles:
    - Finding all ancestor roles (parent, grandparent, etc.)
    - Finding all descendant roles (children, grandchildren, etc.)
    - Detecting circular dependencies
    - Caching hierarchy computations
    
    Example:
        >>> resolver = RoleHierarchyResolver(storage)
        >>> effective_roles = resolver.get_effective_roles(['role_editor'])
        >>> # Returns ['role_editor', 'role_viewer'] if editor inherits from viewer
    """
    
    def __init__(
        self, 
        storage: IStorageProvider,
        max_depth: int = 10
    ):
        """Initialize the hierarchy resolver.
        
        Args:
            storage: Storage provider for role data
            max_depth: Maximum hierarchy depth to prevent infinite loops
        """
        self._storage = storage
        self._max_depth = max_depth
        self._hierarchy_cache: Dict[str, RoleHierarchy] = {}
    
    def get_effective_roles(
        self, 
        role_ids: List[str],
        domain: Optional[str] = None
    ) -> List[str]:
        """Get all effective roles including inherited ones.
        
        Args:
            role_ids: Direct role IDs assigned to user
            domain: Optional domain filter
            
        Returns:
            List of all role IDs including inherited roles
            
        Example:
            >>> # User has 'editor' role
            >>> # 'editor' inherits from 'viewer'
            >>> # 'viewer' inherits from 'member'
            >>> resolver.get_effective_roles(['role_editor'])
            ['role_editor', 'role_viewer', 'role_member']
        """
        effective = set(role_ids)
        
        for role_id in role_ids:
            try:
                hierarchy = self._resolve_hierarchy(role_id, domain)
                effective.update(hierarchy.ancestors)
            except RoleNotFound:
                # Skip roles that don't exist
                continue
        
        return list(effective)
    
    def get_role_hierarchy(
        self, 
        role_id: str,
        domain: Optional[str] = None
    ) -> RoleHierarchy:
        """Get the complete hierarchy for a role.
        
        Args:
            role_id: The role to analyze
            domain: Optional domain filter
            
        Returns:
            RoleHierarchy object with ancestors and descendants
        """
        return self._resolve_hierarchy(role_id, domain)
    
    def is_parent_of(self, parent_id: str, child_id: str) -> bool:
        """Check if one role is an ancestor of another.
        
        Args:
            parent_id: Potential parent role
            child_id: Potential child role
            
        Returns:
            True if parent_id is an ancestor of child_id
        """
        try:
            hierarchy = self._resolve_hierarchy(child_id)
            return parent_id in hierarchy.ancestors
        except RoleNotFound:
            return False
    
    def get_descendants(
        self, 
        role_id: str,
        domain: Optional[str] = None
    ) -> List[str]:
        """Get all descendant roles (children, grandchildren, etc.).
        
        Args:
            role_id: The parent role
            domain: Optional domain filter
            
        Returns:
            List of all descendant role IDs
        """
        try:
            hierarchy = self._resolve_hierarchy(role_id, domain)
            return hierarchy.descendants
        except RoleNotFound:
            return []
    
    def clear_cache(self) -> None:
        """Clear the hierarchy cache.
        
        Call this when roles are modified to ensure fresh data.
        """
        self._hierarchy_cache.clear()
    
    def _resolve_hierarchy(
        self, 
        role_id: str,
        domain: Optional[str] = None
    ) -> RoleHierarchy:
        """Resolve the complete hierarchy for a role.
        
        This method computes ancestors and descendants, caching results
        for performance.
        """
        cache_key = f"{role_id}:{domain}"
        
        if cache_key in self._hierarchy_cache:
            return self._hierarchy_cache[cache_key]
        
        # Get ancestors (walk up the tree)
        ancestors = self._get_ancestors(role_id, domain)
        
        # Get descendants (walk down the tree)
        descendants = self._get_descendants(role_id, domain)
        
        # Calculate depth
        depth = len(ancestors)
        
        hierarchy = RoleHierarchy(
            role_id=role_id,
            ancestors=ancestors,
            descendants=descendants,
            depth=depth
        )
        
        self._hierarchy_cache[cache_key] = hierarchy
        return hierarchy
    
    def _get_ancestors(
        self, 
        role_id: str,
        domain: Optional[str] = None
    ) -> List[str]:
        """Walk up the role hierarchy to find all ancestors.
        
        Returns ancestors in order from immediate parent to root.
        """
        ancestors = []
        current_id = role_id
        visited = set()
        
        for _ in range(self._max_depth):
            if current_id in visited:
                raise CircularDependencyError(
                    f"Circular dependency detected at role {current_id}"
                )
            
            visited.add(current_id)
            
            try:
                role = self._storage.get_role(current_id)
            except RoleNotFound:
                break
            
            # Check domain match
            if domain is not None and role.domain != domain:
                break
            
            # Add parent if exists
            if role.parent_id:
                ancestors.append(role.parent_id)
                current_id = role.parent_id
            else:
                break
        
        if len(ancestors) >= self._max_depth:
            raise CircularDependencyError(
                f"Role hierarchy exceeds maximum depth of {self._max_depth}"
            )
        
        return ancestors
    
    def _get_descendants(
        self, 
        role_id: str,
        domain: Optional[str] = None
    ) -> List[str]:
        """Walk down the role hierarchy to find all descendants.
        
        Returns descendants in breadth-first order.
        """
        descendants = []
        queue = [role_id]
        visited = set()
        
        while queue and len(descendants) < self._max_depth * 10:
            current_id = queue.pop(0)
            
            if current_id in visited:
                raise CircularDependencyError(
                    f"Circular dependency detected at role {current_id}"
                )
            
            visited.add(current_id)
            
            # Find children (roles where parent_id == current_id)
            children = self._find_children(current_id, domain)
            
            for child_id in children:
                if child_id not in descendants:
                    descendants.append(child_id)
                    queue.append(child_id)
        
        return descendants
    
    def _find_children(
        self, 
        parent_id: str,
        domain: Optional[str] = None
    ) -> List[str]:
        """Find all direct children of a role."""
        children = []
        
        # Get all roles and filter
        all_roles = self._storage.list_roles(domain=domain, limit=1000)
        
        for role in all_roles:
            if role.parent_id == parent_id:
                children.append(role.id)
        
        return children
    
    def validate_hierarchy(self, role_id: str, parent_id: Optional[str] = None) -> bool:
        """Validate that a role's hierarchy is valid (no cycles).
        
        Args:
            role_id: Role to validate
            parent_id: Optional parent ID to check (for future assignment)
            
        Returns:
            True if valid, raises CircularDependencyError if invalid
        """
        try:
            if parent_id:
                # Check if adding parent_id would create a cycle
                # by seeing if role_id is an ancestor of parent_id
                parent_ancestors = self._get_ancestors(parent_id, None)
                if role_id in parent_ancestors:
                    raise CircularDependencyError(
                        f"Role {role_id} is already an ancestor of {parent_id}"
                    )
            else:
                self._resolve_hierarchy(role_id)
            return True
        except CircularDependencyError as e:
            # Re-raise with additional context
            raise CircularDependencyError(str(e)) from e
    
    def get_inherited_permissions(self, role: Any) -> Set[str]:
        """Get all permissions including inherited from parent roles.
        
        Args:
            role: Role object with id and permissions attributes
            
        Returns:
            Set of all permission IDs (direct + inherited)
        """
        all_permissions = set(role.permissions)
        
        # Get all ancestor roles
        try:
            ancestors = self._get_ancestors(role.id, getattr(role, 'domain', None))
            
            # Collect permissions from all ancestors
            for ancestor_id in ancestors:
                try:
                    ancestor_role = self._storage.get_role(ancestor_id)
                    all_permissions.update(ancestor_role.permissions)
                except Exception:
                    continue
        except Exception:
            pass
        
        return all_permissions
    
    def get_role_chain(self, role_id: str) -> List[Any]:
        """Get complete role inheritance chain.
        
        Args:
            role_id: Starting role ID
            
        Returns:
            List of role objects from leaf to root
        """
        chain = []
        
        try:
            # Get the starting role
            role = self._storage.get_role(role_id)
            chain.append(role)
            
            # Get ancestors
            ancestors = self._get_ancestors(role_id, getattr(role, 'domain', None))
            
            # Fetch each ancestor role
            for ancestor_id in ancestors:
                try:
                    ancestor = self._storage.get_role(ancestor_id)
                    chain.append(ancestor)
                except Exception:
                    continue
        except Exception:
            pass
        
        return chain
    
    def get_hierarchy_depth(self, role_id: str) -> int:
        """Get depth of role in hierarchy (0 = root).
        
        Args:
            role_id: Role to check
            
        Returns:
            Depth (0 for root roles with no parent)
        """
        try:
            hierarchy = self._resolve_hierarchy(role_id, None)
            return hierarchy.depth
        except Exception:
            return 0
