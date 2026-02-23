"""
Property-based tests for RBAC authorization logic.

Tests core authorization invariants that should hold for any input.
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from hypothesis import HealthCheck

from rbac import RBAC, User, Role, Permission, Resource, RoleAssignment
from rbac.core.models import EntityStatus

# Mark all tests in this module as property tests
pytestmark = pytest.mark.property


# Strategies
@st.composite
def user_ids(draw):
    """Generate valid user IDs."""
    user_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-@.'
    )))
    assume(user_id.strip())
    return user_id.strip()


@st.composite
def actions(draw):
    """Generate valid actions."""
    return draw(st.sampled_from([
        "read", "write", "delete", "create", "update",
        "execute", "admin", "view", "edit", "publish"
    ]))


@st.composite
def resource_types(draw):
    """Generate valid resource types."""
    return draw(st.sampled_from([
        "document", "file", "database", "api", "service",
        "user", "role", "permission", "config", "system"
    ]))


class TestAuthorizationInvariants:
    """Test authorization invariants using property-based testing."""
    
    @given(
        user_id=user_ids(),
        action=actions(),
        resource_type=resource_types()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_no_permissions_means_no_access(self, user_id, action, resource_type):
        """User with no roles/permissions should never have access."""
        rbac = RBAC(storage='memory')
        
        # Create user with no roles
        user = User(
            id=user_id,
            name=user_id,
            email=f"{user_id}@example.com"
        )
        rbac._storage.store_user(user)
        
        # Check authorization
        result = rbac.can(user_id, action, resource_type)
        
        # Should always be False
        assert result is False
    
    @given(
        user_id=user_ids(),
        action=actions(),
        resource_type=resource_types()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_explicit_permission_grants_access(self, user_id, action, resource_type):
        """User with explicit permission should have access."""
        rbac = RBAC(storage='memory')
        
        # Create user
        user = User(
            id=user_id,
            name=user_id,
            email=f"{user_id}@example.com"
        )
        rbac._storage.store_user(user)
        
        # Create resource
        resource = Resource(
            id=f"resource_{resource_type}_1",
            type=resource_type
        )
        rbac._storage.store_resource(resource)
        
        # Create permission
        permission = Permission(
            id=f"perm_{user_id}_{action}",
            action=action,
            resource_type=resource.type
        )
        rbac._storage.store_permission(permission)
        
        # Create role with permission
        role = Role(
            id=f"role_{user_id}",
            name=f"Role for {user_id}",
            permissions={permission}
        )
        rbac._storage.store_role(role)
        
        # Assign role to user
        assignment = RoleAssignment(
            user_id=user_id,
            role_id=role.id
        )
        rbac._storage.store_role_assignment(assignment)
        
        # Check authorization
        result = rbac.can(user_id, action, resource_type)
        
        # Should have access
        assert result is True
    
    @given(
        user_id=user_ids(),
        action1=actions(),
        action2=actions()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_permission_is_action_specific(self, user_id, action1, action2):
        """Permission for one action should not grant another action."""
        assume(action1 != action2)
        
        rbac = RBAC(storage='memory')
        
        # Create user
        user = User(
            id=user_id,
            name=user_id,
            email=f"{user_id}@example.com"
        )
        rbac._storage.store_user(user)
        
        # Create resource
        resource = Resource(
            id="resource_1",
            type="document"
        )
        rbac._storage.store_resource(resource)
        
        # Create permission for action1 only
        permission = Permission(
            id=f"perm_{action1}",
            action=action1,
            resource_type=resource.type
        )
        rbac._storage.store_permission(permission)
        
        # Create role with permission
        role = Role(
            id="role_1",
            name="Test Role",
            permissions={permission}
        )
        rbac._storage.store_role(role)
        
        # Assign role
        assignment = RoleAssignment(
            user_id=user_id,
            role_id=role.id
        )
        rbac._storage.store_role_assignment(assignment)
        
        # Should have action1
        assert rbac.can(user_id, action1, "document") is True
        
        # Should NOT have action2
        assert rbac.can(user_id, action2, "document") is False
    
    @given(
        user_id=user_ids(),
        action=actions(),
        resource_type=resource_types()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_suspended_user_has_no_access(self, user_id, action, resource_type):
        """Suspended user should never have access regardless of permissions."""
        rbac = RBAC(storage='memory')
        
        # Create suspended user
        user = User(
            id=user_id,
            name=user_id,
            email=f"{user_id}@example.com",
            status=EntityStatus.SUSPENDED
        )
        rbac._storage.store_user(user)
        
        # Create resource
        resource = Resource(
            id="resource_1",
            type=resource_type
        )
        rbac._storage.store_resource(resource)
        
        # Create permission
        permission = Permission(
            id=f"perm_{action}",
            action=action,
            resource_type=resource.type
        )
        rbac._storage.store_permission(permission)
        
        # Create role with permission
        role = Role(
            id="role_1",
            name="Test Role",
            permissions={permission}
        )
        rbac._storage.store_role(role)
        
        # Assign role
        assignment = RoleAssignment(
            user_id=user_id,
            role_id=role.id
        )
        rbac._storage.store_role_assignment(assignment)
        
        # Suspended user should have no access
        result = rbac.can(user_id, action, resource_type)
        assert result is False
    
    @given(
        user_id=user_ids(),
        action=actions(),
        resource_type=resource_types()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
    def test_authorization_is_deterministic(self, user_id, action, resource_type):
        """Same authorization check should always return same result."""
        rbac = RBAC(storage='memory')
        
        # Create user
        user = User(
            id=user_id,
            name=user_id,
            email=f"{user_id}@example.com"
        )
        rbac._storage.store_user(user)
        
        # Check authorization multiple times
        result1 = rbac.can(user_id, action, resource_type)
        result2 = rbac.can(user_id, action, resource_type)
        result3 = rbac.can(user_id, action, resource_type)
        
        # All results should be identical
        assert result1 == result2 == result3
    
    @given(
        user_id=user_ids(),
        num_roles=st.integers(min_value=1, max_value=5)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=30)
    def test_multiple_roles_accumulate_permissions(self, user_id, num_roles):
        """User with multiple roles should have all permissions combined."""
        rbac = RBAC(storage='memory')
        
        # Create user
        user = User(
            id=user_id,
            name=user_id,
            email=f"{user_id}@example.com"
        )
        rbac._storage.store_user(user)
        
        # Create resource
        resource = Resource(
            id="resource_1",
            type="document"
        )
        rbac._storage.store_resource(resource)
        
        actions_granted = []
        
        # Create multiple roles, each with a different permission
        for i in range(num_roles):
            action = f"action_{i}"
            actions_granted.append(action)
            
            permission = Permission(
                id=f"perm_{i}",
                action=action,
                resource_type=resource.type
            )
            rbac._storage.store_permission(permission)
            
            role = Role(
                id=f"role_{i}",
                name=f"Role {i}",
                permissions={permission}
            )
            rbac._storage.store_role(role)
            
            assignment = RoleAssignment(
                user_id=user_id,
                role_id=role.id
            )
            rbac._storage.store_role_assignment(assignment)
        
        # User should have all actions
        for action in actions_granted:
            assert rbac.can(user_id, action, "document") is True
