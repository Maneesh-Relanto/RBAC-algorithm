"""
Basic RBAC Example

This example demonstrates the core features of the RBAC system:
- Creating users, roles, and permissions
- Assigning roles to users
- Checking permissions
- Simple authorization
"""

from rbac import RBAC
from datetime import datetime, timedelta


def main():
    print("=" * 70)
    print("RBAC Algorithm - Basic Example")
    print("=" * 70)
    print()
    
    # ==================== Initialize RBAC ====================
    print("1. Initializing RBAC with in-memory storage...")
    rbac = RBAC(storage='memory')
    print("   ✓ RBAC initialized")
    print()
    
    # ==================== Create Permissions ====================
    print("2. Creating permissions...")
    
    # Document permissions
    perm_doc_read = rbac.create_permission(
        permission_id="perm_doc_read",
        resource_type="document",
        action="read",
        description="Read documents"
    )
    print(f"   ✓ Created permission: {perm_doc_read.id}")
    
    perm_doc_write = rbac.create_permission(
        permission_id="perm_doc_write",
        resource_type="document",
        action="write",
        description="Write/edit documents"
    )
    print(f"   ✓ Created permission: {perm_doc_write.id}")
    
    perm_doc_delete = rbac.create_permission(
        permission_id="perm_doc_delete",
        resource_type="document",
        action="delete",
        description="Delete documents"
    )
    print(f"   ✓ Created permission: {perm_doc_delete.id}")
    
    # User management permissions
    perm_user_read = rbac.create_permission(
        permission_id="perm_user_read",
        resource_type="user",
        action="read",
        description="View user profiles"
    )
    print(f"   ✓ Created permission: {perm_user_read.id}")
    print()
    
    # ==================== Create Roles ====================
    print("3. Creating roles with hierarchy...")
    
    # Base role - Viewer (can only read documents)
    role_viewer = rbac.create_role(
        role_id="role_viewer",
        name="Viewer",
        permissions=["perm_doc_read"],
        description="Can view documents"
    )
    print(f"   ✓ Created role: {role_viewer.name} (permissions: read)")
    
    # Editor role (inherits from Viewer, adds write)
    role_editor = rbac.create_role(
        role_id="role_editor",
        name="Editor",
        permissions=["perm_doc_read", "perm_doc_write"],
        parent_id="role_viewer",  # Inherits from Viewer
        description="Can view and edit documents"
    )
    print(f"   ✓ Created role: {role_editor.name} (inherits from Viewer, adds write)")
    
    # Admin role (inherits from Editor, adds delete and user management)
    role_admin = rbac.create_role(
        role_id="role_admin",
        name="Administrator",
        permissions=[
            "perm_doc_read",
            "perm_doc_write",
            "perm_doc_delete",
            "perm_user_read"
        ],
        parent_id="role_editor",  # Inherits from Editor
        description="Full access to documents and users"
    )
    print(f"   ✓ Created role: {role_admin.name} (inherits from Editor, adds delete & user mgmt)")
    print()
    
    # ==================== Create Users ====================
    print("4. Creating users...")
    
    user_alice = rbac.create_user(
        user_id="user_alice",
        email="alice@example.com",
        name="Alice Johnson",
        attributes={"department": "engineering", "level": 5}
    )
    print(f"   ✓ Created user: {user_alice.name} ({user_alice.email})")
    
    user_bob = rbac.create_user(
        user_id="user_bob",
        email="bob@example.com",
        name="Bob Smith",
        attributes={"department": "marketing", "level": 3}
    )
    print(f"   ✓ Created user: {user_bob.name} ({user_bob.email})")
    
    user_carol = rbac.create_user(
        user_id="user_carol",
        email="carol@example.com",
        name="Carol Williams",
        attributes={"department": "engineering", "level": 8}
    )
    print(f"   ✓ Created user: {user_carol.name} ({user_carol.email})")
    print()
    
    # ==================== Assign Roles ====================
    print("5. Assigning roles to users...")
    
    # Alice is a Viewer
    rbac.assign_role("user_alice", "role_viewer")
    print(f"   ✓ Assigned role 'Viewer' to Alice")
    
    # Bob is an Editor
    rbac.assign_role("user_bob", "role_editor")
    print(f"   ✓ Assigned role 'Editor' to Bob")
    
    # Carol is an Administrator
    rbac.assign_role("user_carol", "role_admin")
    print(f"   ✓ Assigned role 'Administrator' to Carol")
    print()
    
    # ==================== Check Permissions ====================
    print("6. Checking permissions...")
    print()
    
    # Test different permission checks
    test_cases = [
        ("user_alice", "read", "Alice trying to READ a document"),
        ("user_alice", "write", "Alice trying to WRITE a document"),
        ("user_alice", "delete", "Alice trying to DELETE a document"),
        ("user_bob", "read", "Bob trying to READ a document"),
        ("user_bob", "write", "Bob trying to WRITE a document"),
        ("user_bob", "delete", "Bob trying to DELETE a document"),
        ("user_carol", "read", "Carol trying to READ a document"),
        ("user_carol", "write", "Carol trying to WRITE a document"),
        ("user_carol", "delete", "Carol trying to DELETE a document"),
        ("user_carol", "read", "Carol trying to VIEW a user", "user"),
    ]
    
    for *args, resource_type in [(tc[0], tc[1], tc[2], "document") 
                                   for tc in test_cases[:-1]] + [test_cases[-1]]:
        user_id, action, description = args[:3]
        
        result = rbac.can(user_id, action, resource_type)
        
        status = "✓ ALLOWED" if result else "✗ DENIED"
        print(f"   {status}: {description}")
    
    print()
    
    # ==================== Detailed Check ====================
    print("7. Getting detailed authorization info...")
    print()
    
    result = rbac.check("user_bob", "write", "document")
    
    print(f"   User: user_bob")
    print(f"   Action: write")
    print(f"   Resource: document")
    print(f"   Decision: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print(f"   Reason: {result['reason']}")
    print(f"   Matched Permissions: {', '.join(result['matched_permissions'])}")
    print()
    
    # ==================== Role Hierarchy ====================
    print("8. Demonstrating role hierarchy...")
    print()
    
    # Get Bob's roles (should include inherited roles)
    bob_roles = rbac.get_user_roles("user_bob")
    print(f"   Bob's direct roles: {', '.join(r.name for r in bob_roles)}")
    
    # Get Bob's effective permissions
    bob_permissions = rbac.get_user_permissions("user_bob")
    print(f"   Bob's total permissions: {len(bob_permissions)}")
    for perm in bob_permissions:
        print(f"      - {perm.action} on {perm.resource_type}")
    
    print()
    
    # ==================== Temporary Role Assignment ====================
    print("9. Temporary role assignment...")
    print()
    
    # Give Alice temporary admin access for 1 hour
    expires_at = datetime.utcnow() + timedelta(hours=1)
    rbac.assign_role(
        "user_alice",
        "role_admin",
        granted_by="user_carol",
        expires_at=expires_at
    )
    
    print(f"   ✓ Granted Alice temporary admin access")
    print(f"      Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Check Alice's new permissions
    can_delete = rbac.can("user_alice", "delete", "document")
    print(f"   Alice can now delete documents: {can_delete}")
    print()
    
    # ==================== Summary ====================
    print("10. System Summary")
    print()
    
    stats = rbac.storage.get_stats()
    print(f"   Total Users: {stats['users']}")
    print(f"   Total Roles: {stats['roles']}")
    print(f"   Total Permissions: {stats['permissions']}")
    print(f"   Total Role Assignments: {stats['role_assignments']}")
    print()
    
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
