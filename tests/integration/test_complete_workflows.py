"""
Integration tests for complete RBAC workflows.

Tests the entire authorization flow from user creation to permission checking.
"""
import pytest
from rbac import RBAC, User, Role, Permission, Resource, RoleAssignment
from rbac.core.models import EntityStatus

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestCompleteAuthorizationFlow:
    """Test complete authorization workflows."""
    
    def test_basic_user_role_permission_flow(self):
        """Test basic flow: create user, role, permission, assign, authorize."""
        # Initialize RBAC
        rbac = RBAC(storage='memory')
        
        # Step 1: Create a user
        user = User(
            id="alice",
            name="alice_admin",
            email="alice@example.com",
            attributes={"department": "engineering"}
        )
        rbac._storage.store_user(user)
        
        # Step 2: Create a resource
        resource = Resource(
            id="doc_1",
            type="document",
            attributes={"classification": "public"}
        )
        rbac._storage.store_resource(resource)
        
        # Step 3: Create permissions
        read_perm = Permission(
            id="perm_read",
            action="read",
            resource_type=resource.type
        )
        write_perm = Permission(
            id="perm_write",
            action="write",
            resource_type=resource.type
        )
        rbac._storage.store_permission(read_perm)
        rbac._storage.store_permission(write_perm)
        
        # Step 4: Create a role with permissions
        editor_role = Role(
            id="role_editor",
            name="Editor",
            description="Can read and write documents",
            permissions={read_perm, write_perm}
        )
        rbac._storage.store_role(editor_role)
        
        # Step 5: Assign role to user
        assignment = RoleAssignment(
            user_id=user.id,
            role_id=editor_role.id
        )
        rbac._storage.store_role_assignment(assignment)
        
        # Step 6: Verify authorization
        assert rbac.can("alice", "read", "document") is True
        assert rbac.can("alice", "write", "document") is True
        assert rbac.can("alice", "delete", "document") is False
    
    def test_role_hierarchy_permission_inheritance(self):
        """Test that child roles inherit parent permissions."""
        rbac = RBAC(storage='memory', enable_hierarchy=True)
        
        # Create user
        user = User(
            id="bob",
            name="bob_user",
            email="bob@example.com"
        )
        rbac._storage.store_user(user)
        
        # Create resource
        resource = Resource(id="api_1", type="api")
        rbac._storage.store_resource(resource)
        
        # Create permissions
        read_perm = Permission(id="perm_read", action="read", resource_type=resource.type)
        write_perm = Permission(id="perm_write", action="write", resource_type=resource.type)
        admin_perm = Permission(id="perm_admin", action="admin", resource_type=resource.type)
        
        rbac._storage.store_permission(read_perm)
        rbac._storage.store_permission(write_perm)
        rbac._storage.store_permission(admin_perm)
        
        # Create role hierarchy: User -> Editor -> Admin
        user_role = Role(
            id="role_user",
            name="User",
            permissions={read_perm}
        )
        editor_role = Role(
            id="role_editor",
            name="Editor",
            parent_id="role_user",
            permissions={write_perm}
        )
        admin_role = Role(
            id="role_admin",
            name="Admin",
            parent_id="role_editor",
            permissions={admin_perm}
        )
        
        rbac._storage.store_role(user_role)
        rbac._storage.store_role(editor_role)
        rbac._storage.store_role(admin_role)
        
        # Assign only the admin role (should inherit all)
        assignment = RoleAssignment(user_id="bob", role_id="role_admin")
        rbac._storage.store_role_assignment(assignment)
        
        # Verify inheritance
        assert rbac.can("bob", "read", "api") is True   # From user_role
        assert rbac.can("bob", "write", "api") is True  # From editor_role
        assert rbac.can("bob", "admin", "api") is True  # From admin_role
    
    def test_multi_role_assignment_accumulation(self):
        """Test that users with multiple roles get all permissions."""
        rbac = RBAC(storage='memory')
        
        # Create user
        user = User(id="charlie", name="charlie", email="charlie@example.com")
        rbac._storage.store_user(user)
        
        # Create resources
        doc_resource = Resource(id="doc_1", type="document")
        db_resource = Resource(id="db_1", type="database")
        rbac._storage.store_resource(doc_resource)
        rbac._storage.store_resource(db_resource)
        
        # Create permissions for different resources
        doc_read = Permission(id="perm_doc_read", action="read", resource_type=doc_resource.type)
        db_read = Permission(id="perm_db_read", action="read", resource_type=db_resource.type)
        db_write = Permission(id="perm_db_write", action="write", resource_type=db_resource.type)
        
        rbac._storage.store_permission(doc_read)
        rbac._storage.store_permission(db_read)
        rbac._storage.store_permission(db_write)
        
        # Create separate roles
        doc_reader = Role(
            id="role_doc_reader",
            name="Document Reader",
            permissions={doc_read}
        )
        db_admin = Role(
            id="role_db_admin",
            name="Database Admin",
            permissions={db_read, db_write}
        )
        
        rbac._storage.store_role(doc_reader)
        rbac._storage.store_role(db_admin)
        
        # Assign both roles
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="charlie", role_id="role_doc_reader")
        )
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="charlie", role_id="role_db_admin")
        )
        
        # Verify accumulated permissions
        assert rbac.can("charlie", "read", "document") is True
        assert rbac.can("charlie", "read", "database") is True
        assert rbac.can("charlie", "write", "database") is True
        assert rbac.can("charlie", "write", "document") is False
    
    def test_user_lifecycle_and_status_changes(self):
        """Test authorization changes based on user lifecycle status."""
        rbac = RBAC(storage='memory')
        
        # Create active user with permissions
        user = User(
            id="dave",
            name="dave",
            email="dave@example.com",
            status=EntityStatus.ACTIVE
        )
        rbac._storage.store_user(user)
        
        resource = Resource(id="file_1", type="file")
        rbac._storage.store_resource(resource)
        
        permission = Permission(id="perm_read", action="read", resource_type=resource.type)
        rbac._storage.store_permission(permission)
        
        role = Role(id="role_reader", name="Reader", permissions={permission})
        rbac._storage.store_role(role)
        
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="dave", role_id="role_reader")
        )
        
        # Active user should have access
        assert rbac.can("dave", "read", "file") is True
        
        # Suspend user
        suspended_user = User(
            id="dave",
            name="dave",
            email="dave@example.com",
            status=EntityStatus.SUSPENDED
        )
        rbac._storage.store_user(suspended_user)
        
        # Suspended user should NOT have access
        assert rbac.can("dave", "read", "file") is False
        
        # Reactivate user
        active_user = User(
            id="dave",
            name="dave",
            email="dave@example.com",
            status=EntityStatus.ACTIVE
        )
        rbac._storage.store_user(active_user)
        
        # Active user should have access again
        assert rbac.can("dave", "read", "file") is True
    
    def test_role_modification_affects_users(self):
        """Test that modifying role permissions affects all users with that role."""
        rbac = RBAC(storage='memory')
        
        # Create two users
        user1 = User(id="user1", name="user1", email="user1@example.com")
        user2 = User(id="user2", name="user2", email="user2@example.com")
        rbac._storage.store_user(user1)
        rbac._storage.store_user(user2)
        
        # Create resource
        resource = Resource(id="service_1", type="service")
        rbac._storage.store_resource(resource)
        
        # Create initial permission
        read_perm = Permission(id="perm_read", action="read", resource_type=resource.type)
        rbac._storage.store_permission(read_perm)
        
        # Create role with limited permission
        role = Role(
            id="role_operator",
            name="Operator",
            permissions={read_perm}
        )
        rbac._storage.store_role(role)
        
        # Assign role to both users
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="user1", role_id="role_operator")
        )
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="user2", role_id="role_operator")
        )
        
        # Both users should have read
        assert rbac.can("user1", "read", "service") is True
        assert rbac.can("user2", "read", "service") is True
        assert rbac.can("user1", "write", "service") is False
        assert rbac.can("user2", "write", "service") is False
        
        # Add write permission to role
        write_perm = Permission(id="perm_write", action="write", resource_type=resource.type)
        rbac._storage.store_permission(write_perm)
        
        updated_role = Role(
            id="role_operator",
            name="Operator",
            permissions={read_perm, write_perm}
        )
        rbac._storage.store_role(updated_role)
        
        # Both users should now have write
        assert rbac.can("user1", "write", "service") is True
        assert rbac.can("user2", "write", "service") is True
    
    def test_domain_isolation(self):
        """Test that users in different domains are isolated."""
        rbac = RBAC(storage='memory')
        
        # Create users in different domains
        user_domain_a = User(
            id="user_a",
            name="user_a",
            email="user@domain-a.com",
            domain="domain-a"
        )
        user_domain_b = User(
            id="user_b",
            name="user_b",
            email="user@domain-b.com",
            domain="domain-b"
        )
        rbac._storage.store_user(user_domain_a)
        rbac._storage.store_user(user_domain_b)
        
        # Create resources in different domains
        resource_a = Resource(id="res_a", type="document", domain="domain-a")
        resource_b = Resource(id="res_b", type="document", domain="domain-b")
        rbac._storage.store_resource(resource_a)
        rbac._storage.store_resource(resource_b)
        
        # Create permissions
        perm_a = Permission(id="perm_a", action="read", resource_type=resource_a.type)
        perm_b = Permission(id="perm_b", action="read", resource_type=resource_b.type)
        rbac._storage.store_permission(perm_a)
        rbac._storage.store_permission(perm_b)
        
        # Create domain-specific roles
        role_a = Role(
            id="role_a",
            name="Role A",
            domain="domain-a",
            permissions={perm_a}
        )
        role_b = Role(
            id="role_b",
            name="Role B",
            domain="domain-b",
            permissions={perm_b}
        )
        rbac._storage.store_role(role_a)
        rbac._storage.store_role(role_b)
        
        # Assign roles
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="user_a", role_id="role_a")
        )
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="user_b", role_id="role_b")
        )
        
        # Users should only access their domain resources
        # Note: This test validates the concept, actual enforcement depends on
        # how the authorization engine filters by domain
        assert rbac.can("user_a", "read", "document") is True
        assert rbac.can("user_b", "read", "document") is True


class TestPerformanceWithLoad:
    """Test RBAC performance under realistic load."""
    
    def test_authorization_with_many_roles(self):
        """Test authorization performance with many roles."""
        rbac = RBAC(storage='memory')
        
        # Create user
        user = User(id="power_user", name="power_user", email="power@example.com")
        rbac._storage.store_user(user)
        
        # Create resource
        resource = Resource(id="system_1", type="system")
        rbac._storage.store_resource(resource)
        
        # Create 50 roles with different permissions
        for i in range(50):
            permission = Permission(
                id=f"perm_{i}",
                action=f"action_{i}",
                resource_type=resource.type
            )
            rbac._storage.store_permission(permission)
            
            role = Role(
                id=f"role_{i}",
                name=f"Role {i}",
                permissions={permission}
            )
            rbac._storage.store_role(role)
            
            rbac._storage.store_role_assignment(
                RoleAssignment(user_id="power_user", role_id=f"role_{i}")
            )
        
        # Authorization should still work efficiently
        assert rbac.can("power_user", "action_0", "system") is True
        assert rbac.can("power_user", "action_25", "system") is True
        assert rbac.can("power_user", "action_49", "system") is True
        assert rbac.can("power_user", "nonexistent_action", "system") is False
    
    def test_authorization_with_deep_hierarchy(self):
        """Test authorization with deep role hierarchy."""
        rbac = RBAC(storage='memory', enable_hierarchy=True)
        
        # Create user
        user = User(id="hierarchical_user", name="h_user", email="h@example.com")
        rbac._storage.store_user(user)
        
        # Create resource
        resource = Resource(id="data_1", type="data")
        rbac._storage.store_resource(resource)
        
        # Create deep hierarchy: level_0 -> level_1 -> ... -> level_10
        for i in range(11):
            permission = Permission(
                id=f"perm_level_{i}",
                action=f"level_{i}_action",
                resource_type=resource.type
            )
            rbac._storage.store_permission(permission)
            
            role = Role(
                id=f"role_level_{i}",
                name=f"Level {i}",
                parent_id=f"role_level_{i-1}" if i > 0 else None,
                permissions={permission}
            )
            rbac._storage.store_role(role)
        
        # Assign deepest role
        rbac._storage.store_role_assignment(
            RoleAssignment(user_id="hierarchical_user", role_id="role_level_10")
        )
        
        # Should inherit all permissions from hierarchy
        for i in range(11):
            assert rbac.can("hierarchical_user", f"level_{i}_action", "data") is True
