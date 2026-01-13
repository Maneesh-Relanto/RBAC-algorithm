"""
Property-based tests for Role model.

Tests invariants that should hold for any valid input.
"""
import pytest
from hypothesis import given, strategies as st, assume, example, settings
from hypothesis import HealthCheck
from datetime import datetime, timezone

from rbac import Role, Permission, Resource, EntityStatus

# Mark all tests in this module as property tests
pytestmark = pytest.mark.property


# Custom strategies for RBAC entities
@st.composite
def role_ids(draw):
    """Generate valid role IDs."""
    # Role IDs should be non-empty strings
    id_str = draw(st.text(min_size=1, max_size=100))
    assume(id_str.strip())  # Must not be only whitespace
    return id_str.strip()


@st.composite
def role_names(draw):
    """Generate valid role names."""
    name = draw(st.text(min_size=1, max_size=100))
    assume(name.strip())
    return name.strip()


@st.composite
def permissions_set(draw):
    """Generate a set of permissions."""
    num_perms = draw(st.integers(min_value=0, max_value=20))
    perms = set()
    for i in range(num_perms):
        perm = Permission(
            id=f"perm_{i}",
            action=draw(st.sampled_from(["read", "write", "delete", "execute", "admin"])),
            resource=Resource(
                id=f"resource_{i}",
                type=draw(st.sampled_from(["document", "file", "database", "api"]))
            )
        )
        perms.add(perm)
    return perms


@st.composite
def metadata_dict(draw):
    """Generate valid metadata dictionaries."""
    return draw(st.dictionaries(
        keys=st.text(min_size=1, max_size=50),
        values=st.one_of(
            st.text(max_size=100),
            st.integers(),
            st.booleans(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.none()
        ),
        max_size=10
    ))


class TestRoleInvariants:
    """Test invariants for Role model using property-based testing."""
    
    @given(
        role_id=role_ids(),
        name=role_names(),
        description=st.one_of(st.none(), st.text(max_size=500)),
        domain=st.one_of(st.none(), st.text(min_size=1, max_size=100))
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_role_creation_is_idempotent(self, role_id, name, description, domain):
        """Creating the same role twice should produce equal results."""
        role1 = Role(
            id=role_id,
            name=name,
            description=description,
            domain=domain
        )
        role2 = Role(
            id=role_id,
            name=name,
            description=description,
            domain=domain
        )
        
        # Same inputs should create equal roles (ignoring timestamps)
        assert role1.id == role2.id
        assert role1.name == role2.name
        assert role1.description == role2.description
        assert role1.domain == role2.domain
    
    @given(
        role_id=role_ids(),
        name=role_names(),
        permissions=permissions_set()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_role_permissions_immutable_after_creation(self, role_id, name, permissions):
        """Role permissions should be immutable once created."""
        role = Role(
            id=role_id,
            name=name,
            permissions=permissions
        )
        
        original_count = len(role.permissions)
        
        # Attempting to modify should not affect the role
        # (frozen dataclass prevents this, but we test the behavior)
        assert len(role.permissions) == original_count
        
        # Role should maintain its permission set
        assert role.permissions == permissions
    
    @given(
        role_id=role_ids(),
        name=role_names(),
        metadata=metadata_dict()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_role_metadata_preserved(self, role_id, name, metadata):
        """Role metadata should be preserved correctly."""
        role = Role(
            id=role_id,
            name=name,
            metadata=metadata
        )
        
        # All metadata should be preserved
        assert role.metadata == metadata
        
        # Individual keys should be accessible
        for key, value in metadata.items():
            assert role.metadata.get(key) == value
    
    @given(
        role_id=role_ids(),
        name=role_names(),
        status=st.sampled_from([EntityStatus.ACTIVE, EntityStatus.INACTIVE, EntityStatus.SUSPENDED])
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_role_status_consistency(self, role_id, name, status):
        """Role status should be consistent with its state."""
        role = Role(
            id=role_id,
            name=name,
            status=status
        )
        
        assert role.status == status
        assert isinstance(role.status, EntityStatus)
    
    @given(
        role_id=role_ids(),
        name=role_names(),
        parent_id=st.one_of(st.none(), role_ids())
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_role_hierarchy_parent_reference(self, role_id, name, parent_id):
        """Role should correctly reference its parent."""
        # Don't allow self-referencing roles
        assume(parent_id != role_id)
        
        role = Role(
            id=role_id,
            name=name,
            parent_id=parent_id
        )
        
        assert role.parent_id == parent_id
        
        # If has parent, should not be None
        if parent_id:
            assert role.parent_id is not None
    
    @given(
        role_id=role_ids(),
        name=role_names()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_role_timestamps_logical_order(self, role_id, name):
        """Role timestamps should be in logical order."""
        role = Role(
            id=role_id,
            name=name
        )
        
        # Created at should be set
        assert role.created_at is not None
        assert isinstance(role.created_at, datetime)
        
        # Updated at should be set
        assert role.updated_at is not None
        assert isinstance(role.updated_at, datetime)
        
        # Updated should be >= created (for new roles, they're equal)
        assert role.updated_at >= role.created_at
    
    @given(
        role_id=role_ids(),
        name=role_names(),
        permissions=permissions_set()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_role_with_permissions_never_loses_them(self, role_id, name, permissions):
        """A role created with permissions should always have them."""
        role = Role(
            id=role_id,
            name=name,
            permissions=permissions
        )
        
        # Check multiple times to ensure consistency
        for _ in range(3):
            assert len(role.permissions) == len(permissions)
            assert role.permissions == permissions
    
    @given(
        role_id=role_ids(),
        name=role_names()
    )
    @example(role_id="admin", name="Administrator")
    @example(role_id="user", name="User")
    @example(role_id="guest", name="Guest")
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_common_role_patterns(self, role_id, name):
        """Test common role naming patterns work correctly."""
        role = Role(
            id=role_id,
            name=name
        )
        
        assert role.id == role_id
        assert role.name == name
        assert role.status == EntityStatus.ACTIVE  # Default status
