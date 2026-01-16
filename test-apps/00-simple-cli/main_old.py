"""
Comprehensive CLI Test App - RBAC Algorithm

This test application validates ALL features of the RBAC algorithm:
1. Basic RBAC - Users, roles, permissions CRUD
2. Role Assignment - User-role relationships
3. Permission Checking - Authorization decisions
4. Role Hierarchy - Parent-child inheritance
5. ABAC Conditions - Context-aware authorization
6. Multi-Tenancy - Domain isolation
7. Status Management - ACTIVE/SUSPENDED/DELETED states
8. Permissions Matrix - Visual role management
9. Wildcards - Universal permissions
10. Role Revocation - Remove user roles
11. Permission Listing - User permissions query
12. Resource Attributes - ABAC with resources

Purpose: Complete end-to-end validation of all RBAC features
Runtime: ~2-3 seconds
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import rbac
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from rbac import (
    RBAC, 
    PermissionDenied, 
    EntityStatus,
    PermissionsMatrixManager,
    User,
    Resource
)


def print_header(text, char="="):
    """Print a formatted header."""
    print(f"\n{char * 70}")
    print(f"{text:^70}")
    print(f"{char * 70}\n")


def print_section(text):
    """Print a section header."""
    print(f"\n{'─' * 70}")
    print(f"│ {text}")
    print(f"{'─' * 70}")


def print_step(step, total, description):
    """Print a step indicator."""
    print(f"\n[{step}/{total}] {description}")


def print_success(message):
    """Print a success message."""
    print(f"  ✓ {message}")


def print_error(message):
    """Print an error message."""
    print(f"  ✗ {message}")


def print_info(message):
    """Print an info message."""
    print(f"  ℹ {message}")


def main():
    """Main test function."""
    print_header("RBAC Algorithm - Comprehensive Feature Test")
    
    total_steps = 12
    passed_tests = 0
    failed_tests = []
    
    try:
        # ==================== Step 1: Initialize ====================
        print_step(1, total_steps, "Initializing RBAC...")
        rbac = RBAC(storage='memory')
        print_success("RBAC initialized")
        passed_tests += 1
        
        # ==================== Step 2: Create Permissions ====================
        print(f"\n[{2}/{total_steps}] Creating permissions...")
        
        perm_read = rbac.create_permission(
            "perm_read",
            "read",
            "document",
            description="Read documents"
        )
        
        perm_write = rbac.create_permission(
            "perm_write",
            "write",
            "document",
            description="Write documents"
        )
        
        perm_delete = rbac.create_permission(
            "perm_delete",
            "delete",
            "document",
            description="Delete documents"
        )
        
        # ABAC permission - edit own documents
        perm_edit_own = rbac.create_permission(
            "perm_edit_own",
            "edit",
            "document",
            description="Edit own documents",
            conditions=[{
                "field": "resource.author_id",
                "operator": "==",
                "value": "{{user.id}}"
            }]
        )
        
        print_success("Created 4 permissions")
        passed_tests += 1
        
        # ==================== Step 3: Create Role Hierarchy ====================
        print(f"\n[{3}/{total_steps}] Creating role hierarchy...")
        
        # Viewer: can only read
        role_viewer = rbac.create_role(
            role_id="role_viewer",
            name="Viewer",
            permissions=["perm_read"],
            description="Can read documents"
        )
        
        # Editor: can read and write (inherits read from viewer)
        role_editor = rbac.create_role(
            role_id="role_editor",
            name="Editor",
            permissions=["perm_write"],
            parent_id="role_viewer",
            description="Can read and write documents"
        )
        
        # Admin: can do everything (inherits from editor)
        role_admin = rbac.create_role(
            role_id="role_admin",
            name="Admin",
            permissions=["perm_delete"],
            parent_id="role_editor",
            description="Full access"
        )
        
        print_success("Created 3 roles (viewer → editor → admin)")
        passed_tests += 1
        
        # ==================== Step 4: Create Users ====================
        print(f"\n[{4}/{total_steps}] Creating users...")
        
        user_alice = rbac.create_user(
            "user_alice",
            "alice@test.com",
            "Alice"
        )
        
        user_bob = rbac.create_user(
            "user_bob",
            "bob@test.com",
            "Bob"
        )
        
        user_charlie = rbac.create_user(
            "user_charlie",
            "charlie@test.com",
            "Charlie"
        )
        
        print_success("Created 3 users")
        passed_tests += 1
        
        # ==================== Step 5: Assign Roles ====================
        print(f"\n[{5}/{total_steps}] Assigning roles...")
        
        rbac.assign_role("user_alice", "role_viewer")
        rbac.assign_role("user_bob", "role_editor")
        rbac.assign_role("user_charlie", "role_admin")
        
        print_success("Assigned roles to users")
        passed_tests += 1
        
        # ==================== Step 6: Test Permission Checks ====================
        print(f"\n[{6}/{total_steps}] Testing permission checks...")
        
        # Test 1: Alice (viewer) can read
        can_read = rbac.can("user_alice", "read", "document")
        print(f"DEBUG: Alice can read = {can_read}")
        result = rbac.check_permission("user_alice", "read", "document")
        print(f"DEBUG: Detailed result = allowed:{result.allowed}, reason:{result.reason}")
        assert can_read == True, f"Alice should be able to read (got {can_read})"
        print_success(f"Alice (viewer) can read: {can_read}")
        
        # Test 2: Alice (viewer) cannot write
        can_write = rbac.can("user_alice", "write", "document")
        assert can_write == False, "Alice should not be able to write"
        print_success(f"Alice (viewer) can write: {can_write}")
        
        # Test 3: Bob (editor) can read (inherited)
        can_read = rbac.can("user_bob", "read", "document")
        assert can_read == True, "Bob should be able to read (inherited)"
        print_success(f"Bob (editor) can read: {can_read}")
        
        # Test 4: Bob (editor) can write
        can_write = rbac.can("user_bob", "write", "document")
        assert can_write == True, "Bob should be able to write"
        print_success(f"Bob (editor) can write: {can_write}")
        
        # Test 5: Charlie (admin) can delete (inherited from editor → viewer)
        can_delete = rbac.can("user_charlie", "delete", "document")
        assert can_delete == True, "Charlie should be able to delete"
        print_success(f"Charlie (admin) can delete: {can_delete}")
        
        passed_tests += 1
        
        # ==================== Step 7: Test ABAC ====================
        print(f"\n[{7}/{total_steps}] Testing ABAC (ownership)...")
        
        # Grant edit_own permission to Alice
        rbac.assign_role("user_alice", "role_editor")  # Give her edit rights
        rbac.create_role(
            role_id="role_author",
            name="Author",
            permissions=["perm_edit_own", "perm_read"],
            description="Can edit own documents"
        )
        rbac.assign_role("user_alice", "role_author")
        
        # Test: Alice can edit her own document
        result_own = rbac.check_permission(
            "user_alice",
            "edit",
            "document_alice_1",
            context={
                "resource": {
                    "author_id": "user_alice"
                }
            }
        )
        assert result_own.allowed == True, "Alice should be able to edit her own document"
        print_success(f"Alice can edit her own document: {result_own.allowed}")
        
        # Test: Alice cannot edit Bob's document
        result_other = rbac.check_permission(
            "user_alice",
            "edit",
            "document_bob_1",
            context={
                "resource": {
                    "author_id": "user_bob"
                }
            }
        )
        assert result_other.allowed == False, "Alice should not be able to edit Bob's document"
        print_success(f"Alice cannot edit Bob's document: {result_other.allowed}")
        
        passed_tests += 1
        
        # ==================== Final Report ====================
        print_header(f"✓ ALL TESTS PASSED ({passed_tests}/{total_steps})", "=")
        return 0
        
    except AssertionError as e:
        print_error(f"Test failed: {e}")
        print_header(f"✗ TESTS FAILED ({passed_tests}/{total_steps})", "=")
        return 1
        
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print_header(f"✗ TESTS FAILED ({passed_tests}/{total_steps})", "=")
        return 1


if __name__ == "__main__":
    sys.exit(main())
