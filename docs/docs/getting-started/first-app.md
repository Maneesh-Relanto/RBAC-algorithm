---
sidebar_position: 3
---

# Build Your First App

Build a complete document management system with RBAC in 15 minutes.

## Project Overview

We'll build a document management system where:
- **Viewers** can read documents
- **Authors** can create and edit their own documents
- **Editors** can edit any document in their department
- **Admins** have full access

## Step 1: Project Setup

Create a new project:

```bash
mkdir my-rbac-app
cd my-rbac-app
pip install rbac-algorithm
```

Create `app.py`:

```python
from rbac import RBAC
from datetime import datetime

# Initialize RBAC
rbac = RBAC()

print("✓ RBAC initialized")
```

## Step 2: Define Permissions

```python
# Document permissions
permissions = {
    "read": rbac.create_permission(
        permission_id="perm_doc_read",
        action="read",
        resource_type="document",
        description="Read documents"
    ),
    "create": rbac.create_permission(
        permission_id="perm_doc_create",
        action="create",
        resource_type="document",
        description="Create new documents"
    ),
    "edit_own": rbac.create_permission(
        permission_id="perm_doc_edit_own",
        action="edit",
        resource_type="document",
        description="Edit own documents",
        conditions=[
            {"field": "resource.author_id", "operator": "==", "value": "{{user.id}}"}
        ]
    ),
    "edit_any": rbac.create_permission(
        permission_id="perm_doc_edit_any",
        action="edit",
        resource_type="document",
        description="Edit any document"
    ),
    "delete": rbac.create_permission(
        permission_id="perm_doc_delete",
        action="delete",
        resource_type="document",
        description="Delete documents"
    )
}

print(f"✓ Created {len(permissions)} permissions")
```

## Step 3: Create Role Hierarchy

```python
# Viewer role - can only read
viewer = rbac.create_role(
    role_id="role_viewer",
    name="Viewer",
    description="Can read documents"
)
rbac.assign_permission_to_role("role_viewer", "perm_doc_read")

# Author role - inherits Viewer, can create and edit own
author = rbac.create_role(
    role_id="role_author",
    name="Author",
    description="Can create and edit own documents",
    parent_id="role_viewer"  # Inherits read permission
)
rbac.assign_permission_to_role("role_author", "perm_doc_create")
rbac.assign_permission_to_role("role_author", "perm_doc_edit_own")

# Editor role - inherits Author, can edit any
editor = rbac.create_role(
    role_id="role_editor",
    name="Editor",
    description="Can edit any document",
    parent_id="role_author"  # Inherits all Author permissions
)
rbac.assign_permission_to_role("role_editor", "perm_doc_edit_any")

# Admin role - inherits Editor, can delete
admin = rbac.create_role(
    role_id="role_admin",
    name="Administrator",
    description="Full document access",
    parent_id="role_editor"  # Inherits all Editor permissions
)
rbac.assign_permission_to_role("role_admin", "perm_doc_delete")

print("✓ Created role hierarchy: Viewer → Author → Editor → Admin")
```

## Step 4: Create Users

```python
users = {
    "alice": rbac.create_user(
        user_id="user_alice",
        email="alice@example.com",
        name="Alice Johnson",
        attributes={"department": "engineering"}
    ),
    "bob": rbac.create_user(
        user_id="user_bob",
        email="bob@example.com",
        name="Bob Smith",
        attributes={"department": "engineering"}
    ),
    "carol": rbac.create_user(
        user_id="user_carol",
        email="carol@example.com",
        name="Carol Williams",
        attributes={"department": "marketing"}
    ),
    "dave": rbac.create_user(
        user_id="user_dave",
        email="dave@example.com",
        name="Dave Brown",
        attributes={"department": "engineering"}
    )
}

print(f"✓ Created {len(users)} users")
```

## Step 5: Assign Roles

```python
# Alice - Viewer
rbac.assign_role_to_user("user_alice", "role_viewer")

# Bob - Author
rbac.assign_role_to_user("user_bob", "role_author")

# Carol - Editor
rbac.assign_role_to_user("user_carol", "role_editor")

# Dave - Admin
rbac.assign_role_to_user("user_dave", "role_admin")

print("✓ Assigned roles to users")
```

## Step 6: Create Documents

```python
documents = {
    "doc1": rbac.create_resource(
        resource_id="resource_doc_001",
        resource_type="document",
        attributes={
            "title": "Engineering Guide",
            "author_id": "user_bob",
            "department": "engineering",
            "status": "published"
        }
    ),
    "doc2": rbac.create_resource(
        resource_id="resource_doc_002",
        resource_type="document",
        attributes={
            "title": "Marketing Strategy",
            "author_id": "user_carol",
            "department": "marketing",
            "status": "draft"
        }
    )
}

print(f"✓ Created {len(documents)} documents")
```

## Step 7: Test Authorization

```python
def test_access(user_id, user_name, action, resource_id, doc_title):
    """Test if a user can perform an action on a resource."""
    result = rbac.check_permission_detailed(
        user_id=user_id,
        action=action,
        resource_id=resource_id
    )
    
    status = "✓ ALLOWED" if result.allowed else "✗ DENIED"
    print(f"{status}: {user_name} trying to {action} '{doc_title}'")
    if result.allowed:
        print(f"         Reason: {result.reason}")
    return result.allowed

print("\n" + "="*70)
print("TESTING AUTHORIZATION")
print("="*70)

# Test 1: Can Alice (Viewer) read documents?
print("\n1. Viewer Access:")
test_access("user_alice", "Alice", "read", "resource_doc_001", "Engineering Guide")
test_access("user_alice", "Alice", "edit", "resource_doc_001", "Engineering Guide")

# Test 2: Can Bob (Author) edit his own document?
print("\n2. Author Access (Own Document):")
test_access("user_bob", "Bob", "read", "resource_doc_001", "Engineering Guide")
test_access("user_bob", "Bob", "edit", "resource_doc_001", "Engineering Guide")

# Test 3: Can Bob edit someone else's document?
print("\n3. Author Access (Others' Document):")
test_access("user_bob", "Bob", "edit", "resource_doc_002", "Marketing Strategy")

# Test 4: Can Carol (Editor) edit any document?
print("\n4. Editor Access:")
test_access("user_carol", "Carol", "edit", "resource_doc_001", "Engineering Guide")
test_access("user_carol", "Carol", "edit", "resource_doc_002", "Marketing Strategy")

# Test 5: Can Dave (Admin) delete documents?
print("\n5. Admin Access:")
test_access("user_dave", "Dave", "delete", "resource_doc_001", "Engineering Guide")
test_access("user_dave", "Dave", "delete", "resource_doc_002", "Marketing Strategy")

# Test 6: Can Bob delete documents?
print("\n6. Author Cannot Delete:")
test_access("user_bob", "Bob", "delete", "resource_doc_001", "Engineering Guide")
```

## Step 8: View User Permissions

```python
def show_user_permissions(user_id, user_name):
    """Display all permissions for a user."""
    roles = rbac.get_user_roles(user_id)
    permissions = rbac.get_user_permissions(user_id)
    
    print(f"\n{user_name}'s Access:")
    print(f"  Roles: {', '.join([r.name for r in roles])}")
    print(f"  Total Permissions: {len(permissions)}")
    for perm in permissions:
        print(f"    - {perm.action} on {perm.resource_type}")

print("\n" + "="*70)
print("USER PERMISSIONS SUMMARY")
print("="*70)

show_user_permissions("user_alice", "Alice (Viewer)")
show_user_permissions("user_bob", "Bob (Author)")
show_user_permissions("user_carol", "Carol (Editor)")
show_user_permissions("user_dave", "Dave (Admin)")
```

## Complete Code

Here's the full `app.py`:

```python
from rbac import RBAC

def main():
    # Initialize
    rbac = RBAC()
    print("✓ RBAC initialized\n")
    
    # Create permissions
    permissions = ["read", "create", "edit_own", "edit_any", "delete"]
    for perm in permissions:
        if perm == "edit_own":
            rbac.create_permission(
                permission_id=f"perm_doc_{perm}",
                action="edit",
                resource_type="document",
                conditions=[{"field": "resource.author_id", "operator": "==", "value": "{{user.id}}"}]
            )
        else:
            action = perm.replace("_any", "").replace("_own", "")
            rbac.create_permission(
                permission_id=f"perm_doc_{perm}",
                action=action,
                resource_type="document"
            )
    print(f"✓ Created {len(permissions)} permissions\n")
    
    # Create role hierarchy
    rbac.create_role("role_viewer", "Viewer")
    rbac.assign_permission_to_role("role_viewer", "perm_doc_read")
    
    rbac.create_role("role_author", "Author", parent_id="role_viewer")
    rbac.assign_permission_to_role("role_author", "perm_doc_create")
    rbac.assign_permission_to_role("role_author", "perm_doc_edit_own")
    
    rbac.create_role("role_editor", "Editor", parent_id="role_author")
    rbac.assign_permission_to_role("role_editor", "perm_doc_edit_any")
    
    rbac.create_role("role_admin", "Administrator", parent_id="role_editor")
    rbac.assign_permission_to_role("role_admin", "perm_doc_delete")
    print("✓ Created role hierarchy\n")
    
    # Create users and assign roles
    users = [
        ("user_alice", "alice@example.com", "Alice Johnson", "role_viewer"),
        ("user_bob", "bob@example.com", "Bob Smith", "role_author"),
        ("user_carol", "carol@example.com", "Carol Williams", "role_editor"),
        ("user_dave", "dave@example.com", "Dave Brown", "role_admin"),
    ]
    
    for user_id, email, name, role in users:
        rbac.create_user(user_id, email, name)
        rbac.assign_role_to_user(user_id, role)
    print(f"✓ Created {len(users)} users\n")
    
    # Create documents
    rbac.create_resource("resource_doc_001", "document", 
                        attributes={"author_id": "user_bob", "title": "Engineering Guide"})
    rbac.create_resource("resource_doc_002", "document",
                        attributes={"author_id": "user_carol", "title": "Marketing Strategy"})
    print("✓ Created 2 documents\n")
    
    # Test access
    print("="*70)
    print("AUTHORIZATION TESTS")
    print("="*70 + "\n")
    
    tests = [
        ("user_alice", "Alice (Viewer)", "read", "resource_doc_001", "Should ALLOW"),
        ("user_alice", "Alice (Viewer)", "edit", "resource_doc_001", "Should DENY"),
        ("user_bob", "Bob (Author)", "edit", "resource_doc_001", "Should ALLOW (own doc)"),
        ("user_bob", "Bob (Author)", "edit", "resource_doc_002", "Should DENY (not owner)"),
        ("user_carol", "Carol (Editor)", "edit", "resource_doc_001", "Should ALLOW"),
        ("user_dave", "Dave (Admin)", "delete", "resource_doc_001", "Should ALLOW"),
    ]
    
    for user_id, user_name, action, resource_id, expectation in tests:
        result = rbac.check_permission(user_id, action, resource_id)
        status = "✓" if result.allowed else "✗"
        print(f"{status} {user_name} {action} - {expectation}")
    
    print("\n✓ Application complete!")

if __name__ == "__main__":
    main()
```

## Run the Application

```bash
python app.py
```

Expected output:
```
✓ RBAC initialized
✓ Created 5 permissions
✓ Created role hierarchy
✓ Created 4 users
✓ Created 2 documents

======================================================================
AUTHORIZATION TESTS
======================================================================

✓ Alice (Viewer) read - Should ALLOW
✗ Alice (Viewer) edit - Should DENY
✓ Bob (Author) edit - Should ALLOW (own doc)
✗ Bob (Author) edit - Should DENY (not owner)
✓ Carol (Editor) edit - Should ALLOW
✓ Dave (Admin) delete - Should ALLOW

✓ Application complete!
```

## What You Learned

- ✅ Creating permissions with conditions (ABAC)
- ✅ Building role hierarchies with inheritance
- ✅ Assigning roles to users
- ✅ Checking permissions programmatically
- ✅ Testing authorization scenarios

## Next Steps

- 📊 [Role Hierarchies](/docs/guides/hierarchical-roles) - Advanced inheritance
- 🔐 [ABAC Guide](/docs/guides/attribute-based) - Complex conditions
- 🏢 [Multi-Tenancy](/docs/guides/multi-tenant) - SaaS applications
- 💾 [Custom Storage](/docs/guides/custom-storage) - Database backends
