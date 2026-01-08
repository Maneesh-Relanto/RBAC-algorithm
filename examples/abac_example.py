"""
Advanced RBAC Example - Attribute-Based Access Control (ABAC)

This example demonstrates advanced features:
- ABAC conditions on permissions
- Context-aware authorization
- Dynamic permission evaluation
- Resource ownership checks
"""

from rbac import RBAC
from datetime import datetime


def main():
    print("=" * 70)
    print("RBAC Algorithm - Advanced ABAC Example")
    print("=" * 70)
    print()
    
    # Initialize RBAC
    print("1. Initializing RBAC with ABAC enabled...")
    rbac = RBAC(
        storage='memory',
        enable_hierarchy=True,
        enable_abac=True  # Enable attribute-based access control
    )
    print("   ✓ RBAC initialized with ABAC")
    print()
    
    # ==================== Create ABAC Permissions ====================
    print("2. Creating ABAC permissions with conditions...")
    print()
    
    # Permission: Read own documents
    perm_read_own = rbac.create_permission(
        permission_id="perm_doc_read_own",
        resource_type="document",
        action="read",
        description="Read own documents",
        conditions={
            "resource.owner_id": {"==": "{{user.id}}"}
        }
    )
    print("   ✓ Created: Read own documents")
    print("      Condition: resource.owner_id == user.id")
    
    # Permission: Read documents in same department
    perm_read_dept = rbac.create_permission(
        permission_id="perm_doc_read_dept",
        resource_type="document",
        action="read",
        description="Read documents in same department",
        conditions={
            "resource.department": {"==": "{{user.department}}"}
        }
    )
    print("   ✓ Created: Read department documents")
    print("      Condition: resource.department == user.department")
    
    # Permission: Edit documents during business hours
    perm_edit_business_hours = rbac.create_permission(
        permission_id="perm_doc_edit_hours",
        resource_type="document",
        action="write",
        description="Edit documents during business hours",
        conditions={
            "time.hour": {">": 8, "<": 18},  # 9 AM to 6 PM
            "resource.owner_id": {"==": "{{user.id}}"}
        }
    )
    print("   ✓ Created: Edit own documents during business hours")
    print("      Conditions: time.hour > 8 AND time.hour < 18 AND resource.owner_id == user.id")
    
    # Permission: Delete only if high level and status is draft
    perm_delete_draft = rbac.create_permission(
        permission_id="perm_doc_delete_draft",
        resource_type="document",
        action="delete",
        description="Delete draft documents (high-level users only)",
        conditions={
            "user.level": {">": 5},
            "resource.status": {"==": "draft"}
        }
    )
    print("   ✓ Created: Delete draft documents (level > 5)")
    print("      Conditions: user.level > 5 AND resource.status == 'draft'")
    
    # Permission: Admin access (no conditions)
    perm_admin = rbac.create_permission(
        permission_id="perm_doc_admin",
        resource_type="document",
        action="*",  # All actions
        description="Full admin access"
    )
    print("   ✓ Created: Full admin access (no conditions)")
    print()
    
    # ==================== Create Roles ====================
    print("3. Creating roles...")
    
    role_member = rbac.create_role(
        role_id="role_member",
        name="Member",
        permissions=["perm_doc_read_own", "perm_doc_edit_hours"],
        description="Regular team member"
    )
    print(f"   ✓ Created role: {role_member.name}")
    print("      - Can read own documents")
    print("      - Can edit own documents during business hours")
    
    role_manager = rbac.create_role(
        role_id="role_manager",
        name="Manager",
        permissions=[
            "perm_doc_read_own",
            "perm_doc_read_dept",
            "perm_doc_edit_hours",
            "perm_doc_delete_draft"
        ],
        description="Team manager"
    )
    print(f"   ✓ Created role: {role_manager.name}")
    print("      - Can read own and department documents")
    print("      - Can delete draft documents")
    
    role_admin = rbac.create_role(
        role_id="role_admin",
        name="Admin",
        permissions=["perm_doc_admin"],
        description="System administrator"
    )
    print(f"   ✓ Created role: {role_admin.name}")
    print("      - Full access to all documents")
    print()
    
    # ==================== Create Users ====================
    print("4. Creating users with attributes...")
    
    user_alice = rbac.create_user(
        user_id="user_alice",
        email="alice@example.com",
        name="Alice Johnson",
        attributes={
            "department": "engineering",
            "level": 3,
            "title": "Software Engineer"
        }
    )
    print(f"   ✓ {user_alice.name} - Engineering, Level 3")
    
    user_bob = rbac.create_user(
        user_id="user_bob",
        email="bob@example.com",
        name="Bob Smith",
        attributes={
            "department": "engineering",
            "level": 7,
            "title": "Engineering Manager"
        }
    )
    print(f"   ✓ {user_bob.name} - Engineering, Level 7")
    
    user_carol = rbac.create_user(
        user_id="user_carol",
        email="carol@example.com",
        name="Carol Williams",
        attributes={
            "department": "marketing",
            "level": 5,
            "title": "Marketing Manager"
        }
    )
    print(f"   ✓ {user_carol.name} - Marketing, Level 5")
    
    user_dave = rbac.create_user(
        user_id="user_dave",
        email="dave@example.com",
        name="Dave Brown",
        attributes={
            "department": "engineering",
            "level": 10,
            "title": "VP Engineering"
        }
    )
    print(f"   ✓ {user_dave.name} - Engineering, Level 10 (Admin)")
    print()
    
    # ==================== Assign Roles ====================
    print("5. Assigning roles...")
    
    rbac.assign_role("user_alice", "role_member")
    print("   ✓ Alice → Member")
    
    rbac.assign_role("user_bob", "role_manager")
    print("   ✓ Bob → Manager")
    
    rbac.assign_role("user_carol", "role_manager")
    print("   ✓ Carol → Manager")
    
    rbac.assign_role("user_dave", "role_admin")
    print("   ✓ Dave → Admin")
    print()
    
    # ==================== Create Resources ====================
    print("6. Creating documents with attributes...")
    
    doc1 = rbac.create_resource(
        resource_id="resource_doc_001",
        resource_type="document",
        attributes={
            "owner_id": "user_alice",
            "department": "engineering",
            "status": "draft",
            "title": "Engineering Design Doc"
        }
    )
    print(f"   ✓ Document 001 - Owner: Alice, Dept: Engineering, Status: Draft")
    
    doc2 = rbac.create_resource(
        resource_id="resource_doc_002",
        resource_type="document",
        attributes={
            "owner_id": "user_bob",
            "department": "engineering",
            "status": "published",
            "title": "Architecture Review"
        }
    )
    print(f"   ✓ Document 002 - Owner: Bob, Dept: Engineering, Status: Published")
    
    doc3 = rbac.create_resource(
        resource_id="resource_doc_003",
        resource_type="document",
        attributes={
            "owner_id": "user_carol",
            "department": "marketing",
            "status": "draft",
            "title": "Marketing Campaign"
        }
    )
    print(f"   ✓ Document 003 - Owner: Carol, Dept: Marketing, Status: Draft")
    print()
    
    # ==================== Test ABAC Authorization ====================
    print("7. Testing ABAC authorization...")
    print()
    
    # Test Case 1: Alice reads her own document
    print("   Test 1: Can Alice read her own document (doc_001)?")
    result = rbac.check(
        "user_alice",
        "read",
        {"type": "document", "id": "resource_doc_001"}
    )
    print(f"      Result: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print(f"      Reason: {result['reason']}")
    print()
    
    # Test Case 2: Alice reads Bob's document (same department)
    print("   Test 2: Can Alice read Bob's document (doc_002, same dept)?")
    result = rbac.check(
        "user_alice",
        "read",
        {"type": "document", "id": "resource_doc_002"}
    )
    print(f"      Result: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print(f"      Reason: {result['reason']}")
    print()
    
    # Test Case 3: Alice reads Carol's document (different department)
    print("   Test 3: Can Alice read Carol's document (doc_003, different dept)?")
    result = rbac.check(
        "user_alice",
        "read",
        {"type": "document", "id": "resource_doc_003"}
    )
    print(f"      Result: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print(f"      Reason: {result['reason']}")
    print()
    
    # Test Case 4: Bob reads documents in his department
    print("   Test 4: Can Bob (Manager) read documents in his department?")
    for doc_id in ["resource_doc_001", "resource_doc_002"]:
        result = rbac.check(
            "user_bob",
            "read",
            {"type": "document", "id": doc_id}
        )
        print(f"      {doc_id}: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print()
    
    # Test Case 5: Bob deletes draft document (level 7 > 5)
    print("   Test 5: Can Bob delete draft document (level 7 > 5)?")
    result = rbac.check(
        "user_bob",
        "delete",
        {"type": "document", "id": "resource_doc_001"}
    )
    print(f"      Result: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print(f"      Reason: {result['reason']}")
    print()
    
    # Test Case 6: Alice deletes draft document (level 3 < 5)
    print("   Test 6: Can Alice delete draft document (level 3 < 5)?")
    result = rbac.check(
        "user_alice",
        "delete",
        {"type": "document", "id": "resource_doc_001"}
    )
    print(f"      Result: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print(f"      Reason: {result['reason']}")
    print()
    
    # Test Case 7: Bob deletes published document
    print("   Test 7: Can Bob delete published document (status != draft)?")
    result = rbac.check(
        "user_bob",
        "delete",
        {"type": "document", "id": "resource_doc_002"}
    )
    print(f"      Result: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print(f"      Reason: {result['reason']}")
    print()
    
    # Test Case 8: Dave (Admin) can do anything
    print("   Test 8: Can Dave (Admin) delete any document?")
    for doc_id in ["resource_doc_001", "resource_doc_002", "resource_doc_003"]:
        result = rbac.check(
            "user_dave",
            "delete",
            {"type": "document", "id": doc_id}
        )
        print(f"      {doc_id}: {'ALLOWED' if result['allowed'] else 'DENIED'}")
    print()
    
    # ==================== Context-Based Authorization ====================
    print("8. Testing time-based conditions...")
    print()
    
    # Simulate different times
    print("   Simulating time: 10:00 AM (business hours)")
    context_morning = {
        "time": {"hour": 10}
    }
    result = rbac.check(
        "user_alice",
        "write",
        {"type": "document", "id": "resource_doc_001"},
        context=context_morning
    )
    print(f"      Alice can edit: {'YES' if result['allowed'] else 'NO'}")
    
    print()
    print("   Simulating time: 8:00 PM (after hours)")
    context_evening = {
        "time": {"hour": 20}
    }
    result = rbac.check(
        "user_alice",
        "write",
        {"type": "document", "id": "resource_doc_001"},
        context=context_evening
    )
    print(f"      Alice can edit: {'YES' if result['allowed'] else 'NO'}")
    print(f"      Reason: {result['reason']}")
    print()
    
    # ==================== Summary ====================
    print("=" * 70)
    print("Key ABAC Features Demonstrated:")
    print("=" * 70)
    print("✓ Resource ownership checks (user.id == resource.owner_id)")
    print("✓ Attribute matching (user.department == resource.department)")
    print("✓ Numeric comparisons (user.level > threshold)")
    print("✓ String matching (resource.status == 'draft')")
    print("✓ Time-based conditions (business hours)")
    print("✓ Multiple conditions (AND logic)")
    print("✓ Wildcard permissions (admin with '*')")
    print("=" * 70)


if __name__ == '__main__':
    main()
