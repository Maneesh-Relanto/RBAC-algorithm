"""
Unit tests for main RBAC class.
"""
import pytest


class TestRBACBasicOperations:
    """Test basic RBAC operations."""
    
    def test_create_user(self, rbac, sample_user):
        """Test creating a user through RBAC."""
        created = rbac.create_user(sample_user)
        assert created.id == sample_user.id
    
    def test_create_role(self, rbac, sample_role):
        """Test creating a role through RBAC."""
        created = rbac.create_role(sample_role)
        assert created.id == sample_role.id
    
    def test_create_permission(self, rbac, sample_permission):
        """Test creating a permission through RBAC."""
        created = rbac.create_permission(sample_permission)
        assert created.id == sample_permission.id
    
    def test_assign_role_to_user(self, rbac, sample_user, sample_role, domain):
        """Test assigning a role to a user."""
        rbac.create_user(sample_user)
        rbac.create_role(sample_role)
        
        result = rbac.assign_role_to_user(sample_user.id, sample_role.id, domain)
        assert result is not None
    
    def test_assign_permission_to_role(self, rbac, sample_role, sample_permission, domain):
        """Test assigning a permission to a role."""
        rbac.create_role(sample_role)
        rbac.create_permission(sample_permission)
        
        result = rbac.assign_permission_to_role(sample_role.id, sample_permission.id, domain)
        assert result is not None


class TestRBACAuthorization:
    """Test authorization checks."""
    
    def test_check_permission_allowed(self, populated_rbac, sample_user, domain):
        """Test permission check that should pass."""
        allowed = populated_rbac.check_permission(
            sample_user.id,
            "read",
            "document",
            domain
        )
        assert allowed is True
    
    def test_check_permission_denied(self, populated_rbac, sample_user, domain):
        """Test permission check that should fail."""
        denied = populated_rbac.check_permission(
            sample_user.id,
            "delete",  # User doesn't have this permission
            "document",
            domain
        )
        assert denied is False
    
    def test_check_permission_nonexistent_user(self, rbac, domain):
        """Test permission check for non-existent user."""
        denied = rbac.check_permission(
            "nonexistent",
            "read",
            "document",
            domain
        )
        assert denied is False


class TestRBACHierarchy:
    """Test role hierarchy functionality."""
    
    def test_create_role_inheritance(self, rbac, domain):
        """Test creating role inheritance."""
        parent = rbac.create_role({"id": "parent", "name": "Parent", "domain": domain})
        child = rbac.create_role({"id": "child", "name": "Child", "domain": domain})
        
        result = rbac.add_role_inheritance(parent.id, child.id, domain)
        assert result is not None
    
    def test_inherited_permissions(self, rbac, sample_user, domain):
        """Test that child roles inherit parent permissions."""
        # Create roles
        parent = rbac.create_role({"id": "parent", "name": "Parent", "domain": domain})
        child = rbac.create_role({"id": "child", "name": "Child", "domain": domain})
        
        # Create permission and assign to parent
        perm = rbac.create_permission({
            "id": "perm1",
            "action": "read",
            "resource": "document",
            "domain": domain
        })
        rbac.assign_permission_to_role(parent.id, perm.id, domain)
        
        # Create inheritance
        rbac.add_role_inheritance(parent.id, child.id, domain)
        
        # Assign child role to user
        rbac.create_user(sample_user)
        rbac.assign_role_to_user(sample_user.id, child.id, domain)
        
        # User should have permission through inheritance
        allowed = rbac.check_permission(sample_user.id, "read", "document", domain)
        assert allowed is True


class TestRBACMultiTenancy:
    """Test multi-tenancy features."""
    
    def test_domain_isolation(self, rbac):
        """Test that different domains are isolated."""
        user1 = rbac.create_user({
            "id": "user1",
            "username": "user1",
            "email": "user1@example.com",
            "domain": "domain1"
        })
        user2 = rbac.create_user({
            "id": "user1",
            "username": "user1",
            "email": "user1@example.com",
            "domain": "domain2"
        })
        
        # Both should exist in their own domains
        assert user1.domain == "domain1"
        assert user2.domain == "domain2"
        
        # Check they don't interfere
        retrieved1 = rbac.get_user("user1", "domain1")
        retrieved2 = rbac.get_user("user1", "domain2")
        
        assert retrieved1.domain == "domain1"
        assert retrieved2.domain == "domain2"


class TestRBACBatchOperations:
    """Test batch operations."""
    
    def test_batch_create_users(self, rbac, domain):
        """Test creating multiple users at once."""
        users = [
            {"id": f"user{i}", "username": f"user{i}", "email": f"user{i}@example.com", "domain": domain}
            for i in range(5)
        ]
        created = rbac.batch_create_users(users)
        assert len(created) == 5
    
    def test_batch_assign_roles(self, rbac, domain):
        """Test assigning roles to multiple users."""
        # Create users and role
        users = [rbac.create_user({
            "id": f"user{i}",
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "domain": domain
        }) for i in range(3)]
        
        role = rbac.create_role({"id": "role1", "name": "Admin", "domain": domain})
        
        # Batch assign
        user_ids = [u.id for u in users]
        results = rbac.batch_assign_roles(user_ids, role.id, domain)
        assert len(results) == 3
