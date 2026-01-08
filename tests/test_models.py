"""
Unit tests for RBAC data models.
"""
import pytest
from src.rbac.core.models.user import User
from src.rbac.core.models.role import Role
from src.rbac.core.models.permission import Permission
from src.rbac.core.models.resource import Resource
from src.rbac.core.models.role_assignment import RoleAssignment


class TestUser:
    """Test cases for User model."""
    
    def test_create_user(self, domain):
        """Test user creation."""
        user = User(
            id="user1",
            username="testuser",
            email="test@example.com",
            domain=domain
        )
        assert user.id == "user1"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.domain == domain
    
    def test_user_with_metadata(self, domain):
        """Test user with metadata."""
        user = User(
            id="user1",
            username="testuser",
            email="test@example.com",
            domain=domain,
            metadata={"department": "engineering", "level": 3}
        )
        assert user.metadata["department"] == "engineering"
        assert user.metadata["level"] == 3
    
    def test_user_equality(self, domain):
        """Test user equality."""
        user1 = User(id="user1", username="test", email="test@example.com", domain=domain)
        user2 = User(id="user1", username="test", email="test@example.com", domain=domain)
        assert user1.id == user2.id
        assert user1.domain == user2.domain


class TestRole:
    """Test cases for Role model."""
    
    def test_create_role(self, domain):
        """Test role creation."""
        role = Role(
            id="role1",
            name="admin",
            description="Administrator role",
            domain=domain
        )
        assert role.id == "role1"
        assert role.name == "admin"
        assert role.description == "Administrator role"
        assert role.domain == domain
    
    def test_role_with_permissions(self, domain):
        """Test role with permissions."""
        role = Role(
            id="role1",
            name="editor",
            description="Editor role",
            domain=domain,
            permissions=["perm1", "perm2"]
        )
        assert len(role.permissions) == 2
        assert "perm1" in role.permissions
        assert "perm2" in role.permissions


class TestPermission:
    """Test cases for Permission model."""
    
    def test_create_permission(self, domain):
        """Test permission creation."""
        perm = Permission(
            id="perm1",
            action="read",
            resource="document",
            domain=domain
        )
        assert perm.id == "perm1"
        assert perm.action == "read"
        assert perm.resource == "document"
        assert perm.domain == domain
    
    def test_permission_with_conditions(self, domain):
        """Test permission with ABAC conditions."""
        perm = Permission(
            id="perm1",
            action="read",
            resource="document",
            domain=domain,
            conditions={"department": {"==": "engineering"}}
        )
        assert perm.conditions is not None
        assert "department" in perm.conditions


class TestResource:
    """Test cases for Resource model."""
    
    def test_create_resource(self, domain):
        """Test resource creation."""
        resource = Resource(
            id="res1",
            type="document",
            domain=domain
        )
        assert resource.id == "res1"
        assert resource.type == "document"
        assert resource.domain == domain
    
    def test_resource_with_attributes(self, domain):
        """Test resource with attributes."""
        resource = Resource(
            id="res1",
            type="document",
            attributes={"classification": "confidential", "owner": "user1"},
            domain=domain
        )
        assert resource.attributes["classification"] == "confidential"
        assert resource.attributes["owner"] == "user1"


class TestRoleAssignment:
    """Test cases for RoleAssignment model."""
    
    def test_create_assignment(self, domain):
        """Test role assignment creation."""
        assignment = RoleAssignment(
            id="assign1",
            user_id="user1",
            role_id="role1",
            domain=domain
        )
        assert assignment.id == "assign1"
        assert assignment.user_id == "user1"
        assert assignment.role_id == "role1"
        assert assignment.domain == domain
