"""
Unit tests for storage implementations.
"""
import pytest
from rbac.storage.memory import MemoryStorage
from rbac import User, Role


class TestMemoryStorage:
    """Test cases for MemoryStorage."""
    
    def test_create_user(self, storage, sample_user):
        """Test creating a user."""
        created = storage.create_user(sample_user)
        assert created.id == sample_user.id
        assert created.username == sample_user.username
    
    def test_get_user(self, storage, sample_user):
        """Test retrieving a user."""
        storage.create_user(sample_user)
        retrieved = storage.get_user(sample_user.id, sample_user.domain)
        assert retrieved is not None
        assert retrieved.id == sample_user.id
    
    def test_list_users(self, storage, domain):
        """Test listing users."""
        user1 = User(id="user1", name="user1", email="user1@example.com", domain=domain)
        user2 = User(id="user2", name="user2", email="user2@example.com", domain=domain)
        storage.create_user(user1)
        storage.create_user(user2)
        
        users = storage.list_users(domain)
        assert len(users) == 2
    
    def test_update_user(self, storage, sample_user):
        """Test updating a user."""
        storage.create_user(sample_user)
        sample_user.email = "updated@example.com"
        updated = storage.update_user(sample_user)
        assert updated.email == "updated@example.com"
    
    def test_delete_user(self, storage, sample_user):
        """Test deleting a user."""
        storage.create_user(sample_user)
        result = storage.delete_user(sample_user.id, sample_user.domain)
        assert result is True
        retrieved = storage.get_user(sample_user.id, sample_user.domain)
        assert retrieved is None
    
    def test_create_role(self, storage, sample_role):
        """Test creating a role."""
        created = storage.create_role(sample_role)
        assert created.id == sample_role.id
        assert created.name == sample_role.name
    
    def test_domain_isolation(self, storage):
        """Test that domains are isolated."""
        user1 = User(id="user1", name="user1", email="user1@example.com", domain="domain1")
        user2 = User(id="user1", name="user1", email="user1@example.com", domain="domain2")
        
        storage.create_user(user1)
        storage.create_user(user2)
        
        # Should be able to retrieve both with different domains
        retrieved1 = storage.get_user("user1", "domain1")
        retrieved2 = storage.get_user("user1", "domain2")
        
        assert retrieved1 is not None
        assert retrieved2 is not None
        assert retrieved1.domain == "domain1"
        assert retrieved2.domain == "domain2"
    
    def test_batch_create_users(self, storage, domain):
        """Test batch user creation."""
        users = [
            User(id=f"user{i}", name=f"user{i}", email=f"user{i}@example.com", domain=domain)
            for i in range(5)
        ]
        created = storage.batch_create_users(users)
        assert len(created) == 5
    
    def test_get_users_by_role(self, storage, domain):
        """Test getting users by role."""
        user = User(id="user1", name="user1", email="user1@example.com", domain=domain)
        role = Role(id="role1", name="admin", description="Admin", domain=domain)
        
        storage.create_user(user)
        storage.create_role(role)
        storage.assign_role_to_user(user.id, role.id, domain)
        
        users = storage.get_users_by_role(role.id, domain)
        assert len(users) == 1
        assert users[0].id == user.id
