"""
PyTest configuration and fixtures for RBAC Algorithm tests.
"""
import pytest
from rbac import User, Role, Permission, Resource, RBAC, RoleAssignment
from rbac.storage.memory import MemoryStorage


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
        name="testuser",
        email="test@example.com",
        domain=domain,
        attributes={"department": "engineering"}
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
        resource_type="document",
        action="read"
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


# Pytest marker registration
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (slower, test component interactions)")
    config.addinivalue_line("markers", "property: Property-based tests using Hypothesis")
    config.addinivalue_line("markers", "slow: Slow tests (may take more than 1 second)")
    config.addinivalue_line("markers", "performance: Performance benchmarks")
    config.addinivalue_line("markers", "security: Security-related tests")
