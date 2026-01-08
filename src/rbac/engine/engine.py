"""Main authorization engine.

Coordinates storage, hierarchy resolution, and policy evaluation
to make authorization decisions.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime

from ..core.protocols import (
    IAuthorizationEngine, 
    IStorageProvider,
    ICacheProvider
)
from ..core.models import User, Permission, Resource
from ..core.exceptions import (
    PermissionDenied, 
    UserNotFound, 
    ResourceNotFound,
    AuthorizationError
)
from .hierarchy import RoleHierarchyResolver
from .evaluator import PolicyEvaluator


@dataclass
class AuthorizationResult:
    """Result of an authorization check."""
    allowed: bool
    reason: str
    matched_permissions: List[str]
    user_id: str
    action: str
    resource_id: Optional[str]
    timestamp: datetime


class AuthorizationEngine(IAuthorizationEngine):
    """Main authorization engine.
    
    This class coordinates all components to make authorization decisions:
    - Fetches user roles from storage
    - Resolves role hierarchies
    - Collects applicable permissions
    - Evaluates ABAC conditions
    - Returns authorization decision
    
    Example:
        >>> engine = AuthorizationEngine(storage)
        >>> result = engine.check_permission(
        ...     user_id="user_123",
        ...     action="read",
        ...     resource_type="document",
        ...     resource_id="doc_456"
        ... )
        >>> if result.allowed:
        ...     # Grant access
    """
    
    def __init__(
        self,
        storage: IStorageProvider,
        cache: Optional[ICacheProvider] = None,
        enable_hierarchy: bool = True,
        enable_abac: bool = True
    ):
        """Initialize the authorization engine.
        
        Args:
            storage: Storage provider for RBAC data
            cache: Optional cache for performance
            enable_hierarchy: Enable role hierarchy resolution
            enable_abac: Enable attribute-based access control
        """
        self._storage = storage
        self._cache = cache
        self._enable_hierarchy = enable_hierarchy
        self._enable_abac = enable_abac
        
        # Initialize components
        self._hierarchy_resolver = RoleHierarchyResolver(storage)
        self._policy_evaluator = PolicyEvaluator()
    
    def check_permission(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AuthorizationResult:
        """Check if a user has permission to perform an action.
        
        Args:
            user_id: ID of the user
            action: Action to perform (e.g., "read", "write")
            resource_type: Type of resource (e.g., "document")
            resource_id: Optional specific resource ID
            context: Optional context for ABAC evaluation
            
        Returns:
            AuthorizationResult with decision and details
            
        Raises:
            UserNotFound: If user doesn't exist
            AuthorizationError: If check fails
        """
        start_time = datetime.utcnow()
        
        # Build context
        full_context = self._build_context(
            user_id, 
            resource_type,
            resource_id, 
            context
        )
        
        # Get user's effective roles
        user_roles = self._get_effective_roles(user_id, full_context)
        
        if not user_roles:
            return AuthorizationResult(
                allowed=False,
                reason="User has no roles assigned",
                matched_permissions=[],
                user_id=user_id,
                action=action,
                resource_id=resource_id,
                timestamp=start_time
            )
        
        # Collect all permissions from roles
        permissions = self._collect_permissions(user_roles)
        
        # Find matching permissions
        matched = self._find_matching_permissions(
            permissions,
            action,
            resource_type,
            full_context
        )
        
        if matched:
            return AuthorizationResult(
                allowed=True,
                reason=f"Allowed by permission(s): {', '.join(matched)}",
                matched_permissions=matched,
                user_id=user_id,
                action=action,
                resource_id=resource_id,
                timestamp=start_time
            )
        else:
            return AuthorizationResult(
                allowed=False,
                reason=f"No matching permission for {action} on {resource_type}",
                matched_permissions=[],
                user_id=user_id,
                action=action,
                resource_id=resource_id,
                timestamp=start_time
            )
    
    def check_permission_batch(
        self,
        user_id: str,
        checks: List[Dict[str, Any]]
    ) -> List[AuthorizationResult]:
        """Check multiple permissions efficiently.
        
        Args:
            user_id: ID of the user
            checks: List of permission checks, each with:
                - action: str
                - resource_type: str
                - resource_id: Optional[str]
                - context: Optional[Dict]
                
        Returns:
            List of AuthorizationResult, one per check
        """
        results = []
        
        # Get user roles once (cached)
        base_context = self._build_context(user_id, None, None, None)
        user_roles = self._get_effective_roles(user_id, base_context)
        permissions = self._collect_permissions(user_roles)
        
        # Perform each check
        for check in checks:
            action = check.get('action')
            resource_type = check.get('resource_type')
            resource_id = check.get('resource_id')
            context = check.get('context', {})
            
            full_context = self._build_context(
                user_id,
                resource_type,
                resource_id,
                context
            )
            
            matched = self._find_matching_permissions(
                permissions,
                action,
                resource_type,
                full_context
            )
            
            results.append(AuthorizationResult(
                allowed=bool(matched),
                reason="Allowed" if matched else "Denied",
                matched_permissions=matched,
                user_id=user_id,
                action=action,
                resource_id=resource_id,
                timestamp=datetime.utcnow()
            ))
        
        return results
    
    def get_user_permissions(
        self,
        user_id: str,
        resource_type: Optional[str] = None,
        domain: Optional[str] = None
    ) -> List[Permission]:
        """Get all permissions available to a user.
        
        Args:
            user_id: ID of the user
            resource_type: Optional filter by resource type
            domain: Optional domain filter
            
        Returns:
            List of Permission objects
        """
        context = {'user': {'id': user_id}, 'domain': domain}
        
        # Get user's roles
        user_roles = self._get_effective_roles(user_id, context)
        
        # Collect permissions
        permissions = self._collect_permissions(user_roles)
        
        # Filter by resource type if specified
        if resource_type:
            permissions = [
                p for p in permissions 
                if p.resource_type == resource_type
            ]
        
        return permissions
    
    def _build_context(
        self,
        user_id: str,
        resource_type: Optional[str],
        resource_id: Optional[str],
        extra_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build a complete context for ABAC evaluation.
        
        Includes:
        - User attributes
        - Resource attributes (if resource_id provided)
        - Time/date
        - Custom context
        """
        context = extra_context.copy() if extra_context else {}
        
        # Add user info
        try:
            user = self._storage.get_user(user_id)
            context['user'] = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'status': user.status.value,
                'domain': user.domain,
                **user.attributes
            }
        except UserNotFound:
            context['user'] = {'id': user_id}
        
        # Add resource info
        if resource_id:
            try:
                resource = self._storage.get_resource(resource_id)
                context['resource'] = {
                    'id': resource.id,
                    'type': resource.type,
                    'domain': resource.domain,
                    **resource.attributes
                }
            except ResourceNotFound:
                context['resource'] = {
                    'id': resource_id,
                    'type': resource_type
                }
        elif resource_type:
            context['resource'] = {'type': resource_type}
        
        # Add temporal context
        now = datetime.utcnow()
        context['time'] = {
            'current': now.isoformat(),
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'timestamp': int(now.timestamp())
        }
        
        return context
    
    def _get_effective_roles(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Get all effective roles for a user.
        
        Includes directly assigned roles and inherited roles.
        """
        domain = context.get('user', {}).get('domain')
        
        # Check cache first
        if self._cache:
            cache_key = f"user_roles:{user_id}:{domain}"
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        
        # Get direct roles
        try:
            user_roles = self._storage.get_user_roles(user_id, domain)
            direct_role_ids = [role.id for role in user_roles]
        except UserNotFound:
            raise
        
        # Resolve hierarchy if enabled
        if self._enable_hierarchy and direct_role_ids:
            effective_role_ids = self._hierarchy_resolver.get_effective_roles(
                direct_role_ids,
                domain
            )
        else:
            effective_role_ids = direct_role_ids
        
        # Cache the result
        if self._cache:
            self._cache.set(cache_key, effective_role_ids, ttl=300)
        
        return effective_role_ids
    
    def _collect_permissions(
        self,
        role_ids: List[str]
    ) -> List[Permission]:
        """Collect all permissions from a list of roles."""
        permission_ids: Set[str] = set()
        
        # Gather permission IDs from all roles
        for role_id in role_ids:
            try:
                role = self._storage.get_role(role_id)
                permission_ids.update(role.permissions)
            except:
                continue
        
        # Fetch permission objects
        permissions = []
        for perm_id in permission_ids:
            try:
                perm = self._storage.get_permission(perm_id)
                permissions.append(perm)
            except:
                continue
        
        return permissions
    
    def _find_matching_permissions(
        self,
        permissions: List[Permission],
        action: str,
        resource_type: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Find permissions that match the requested action and resource.
        
        Returns list of matching permission IDs.
        """
        matched = []
        
        for perm in permissions:
            # Check action and resource type
            if perm.action != action and perm.action != '*':
                continue
            
            if perm.resource_type != resource_type and perm.resource_type != '*':
                continue
            
            # Evaluate ABAC conditions if present
            if self._enable_abac and perm.conditions:
                try:
                    if not self._policy_evaluator.evaluate(
                        perm.conditions, 
                        context
                    ):
                        continue
                except Exception:
                    # Policy evaluation failed = deny
                    continue
            
            matched.append(perm.id)
        
        return matched
    
    def clear_cache(self) -> None:
        """Clear authorization cache.
        
        Call this when roles or permissions are modified.
        """
        if self._cache:
            self._cache.clear()
        
        self._hierarchy_resolver.clear_cache()
