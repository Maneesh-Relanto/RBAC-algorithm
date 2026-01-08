"""
PyTest configuration and fixtures for RBAC Algorithm tests.
"""
import pytest
from src.rbac.core.models.user import User
from src.rbac.core.models.role import Role
from src.rbac.core.models.permission import Permission
from src.rbac.core.models.resource import Resource
from src.rbac.core.models.role_assignment import RoleAssignment
from src.rbac.storage.memory import MemoryStorage
from src.rbac.rbac import RBAC


@pytest.fixture
def domain():
    """Test domain fixture."""
    return "test-domain"


@pytest.fixture
def storage():
    """Memory storage fixture."""
    return MemoryStorage()


@pytest.fixture
def rbac(storage):
    """RBAC instance fixture."""
    return RBAC(storage=storage)


@pytest.fixture
def sample_user(domain):
    """Sample user fixture."""
    return User(
        id="user1",
        username="testuser",
        email="test@example.com",
        domain=domain,
        metadata={"department": "engineering"}
    )


@pytest.fixture
def sample_role(domain):
    """Sample role fixture."""
    return Role(
        id="role1",
        name="admin",
        description="Administrator role",
        domain=domain
    )


@pytest.fixture
def sample_permission(domain):
    """Sample permission fixture."""
    return Permission(
        id="perm1",
        action="read",
        resource="document",
        domain=domain
    )


@pytest.fixture
def sample_resource(domain):
    """Sample resource fixture."""
    return Resource(
        id="res1",
        type="document",
        attributes={"classification": "public"},
        domain=domain
    )


@pytest.fixture
def populated_rbac(rbac, sample_user, sample_role, sample_permission, domain):
    """RBAC instance with test data."""
    # Create entities
    rbac.create_user(sample_user)
    rbac.create_role(sample_role)
    rbac.create_permission(sample_permission)
    
    # Assign permission to role
    rbac.assign_permission_to_role(sample_role.id, sample_permission.id, domain)
    
    # Assign role to user
    rbac.assign_role_to_user(sample_user.id, sample_role.id, domain)
    
    return rbac
