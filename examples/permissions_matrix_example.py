"""
Example: Using the Permissions Matrix

This example demonstrates how to create, view, and edit permission matrices
for role-permission management.
"""

from src.rbac import RBAC
from src.rbac.matrix import PermissionsMatrixManager, MatrixMode


def main():
    """Demonstrate permissions matrix functionality."""
    
    print("=" * 80)
    print("PERMISSIONS MATRIX EXAMPLE")
    print("=" * 80)
    
    # Initialize RBAC
    rbac = RBAC(storage='memory')
    
    # Create sample data
    setup_sample_data(rbac)
    
    # Create matrix manager
    matrix_mgr = PermissionsMatrixManager(rbac._storage)
    
    # Example 1: Read-only matrix view
    print("\n" + "=" * 80)
    print("1. READ-ONLY MATRIX VIEW")
    print("=" * 80)
    
    matrix = matrix_mgr.create_matrix(mode=MatrixMode.READONLY)
    print("\nCurrent Permissions Matrix:")
    matrix_mgr.print_matrix(matrix)
    
    # Example 2: Editable matrix
    print("\n" + "=" * 80)
    print("2. EDITABLE MATRIX - MAKING CHANGES")
    print("=" * 80)
    
    edit_matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)
    print("\nInitial state:")
    matrix_mgr.print_matrix(edit_matrix)
    
    # Make some changes
    print("\nToggling permissions...")
    
    # Give viewer write permission
    print("  • Granting 'Document - Write' to 'Viewer'")
    matrix_mgr.toggle_permission(edit_matrix, "role_viewer", "perm_doc_write")
    
    # Remove delete permission from admin (for demo)
    print("  • Revoking 'Document - Delete' from 'Admin'")
    matrix_mgr.toggle_permission(edit_matrix, "role_admin", "perm_doc_delete")
    
    # Give editor delete permission
    print("  • Granting 'Document - Delete' to 'Editor'")
    matrix_mgr.toggle_permission(edit_matrix, "role_editor", "perm_doc_delete")
    
    print("\nMatrix after changes (before applying):")
    matrix_mgr.print_matrix(edit_matrix)
    
    # Example 3: Apply changes
    print("\n" + "=" * 80)
    print("3. APPLYING CHANGES")
    print("=" * 80)
    
    result = matrix_mgr.apply_changes(edit_matrix)
    print(f"\nResult: {result}")
    
    # Verify changes
    print("\nVerifying changes...")
    final_matrix = matrix_mgr.create_matrix(mode=MatrixMode.READONLY)
    matrix_mgr.print_matrix(final_matrix)
    
    # Example 4: Bulk set permissions
    print("\n" + "=" * 80)
    print("4. BULK PERMISSION CHANGES")
    print("=" * 80)
    
    bulk_matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)
    
    print("\nGranting all document permissions to Admin...")
    matrix_mgr.set_permission(bulk_matrix, "role_admin", "perm_doc_read", True)
    matrix_mgr.set_permission(bulk_matrix, "role_admin", "perm_doc_write", True)
    matrix_mgr.set_permission(bulk_matrix, "role_admin", "perm_doc_delete", True)
    
    print("\nRevoking all user management permissions from Viewer...")
    matrix_mgr.set_permission(bulk_matrix, "role_viewer", "perm_user_view", False)
    
    matrix_mgr.print_matrix(bulk_matrix)
    
    print("\nApplying bulk changes...")
    result = matrix_mgr.apply_changes(bulk_matrix)
    print(f"Result: {result}")
    
    # Example 5: Export matrix data
    print("\n" + "=" * 80)
    print("5. EXPORT MATRIX DATA")
    print("=" * 80)
    
    export_matrix = matrix_mgr.create_matrix()
    data = matrix_mgr.export_matrix_data(export_matrix)
    
    print("\nExported data structure:")
    print(f"  Roles: {len(data['roles'])}")
    print(f"  Permissions: {len(data['permissions'])}")
    print(f"  Active assignments: {len(data['assignments'])}")
    
    print("\nRole-Permission assignments:")
    for assignment in data['assignments']:
        role_name = next(r['name'] for r in data['roles'] if r['id'] == assignment['role_id'])
        perm_info = next(p for p in data['permissions'] if p['id'] == assignment['permission_id'])
        print(f"  • {role_name}: {perm_info['resource_type']}.{perm_info['action']}")
    
    # Example 6: Discard changes
    print("\n" + "=" * 80)
    print("6. DISCARD CHANGES")
    print("=" * 80)
    
    discard_matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)
    print("\nMaking changes...")
    matrix_mgr.toggle_permission(discard_matrix, "role_viewer", "perm_doc_delete")
    matrix_mgr.toggle_permission(discard_matrix, "role_editor", "perm_user_manage")
    
    print(f"Changes pending: {discard_matrix.get_change_count()}")
    matrix_mgr.print_matrix(discard_matrix)
    
    print("\nDiscarding changes...")
    matrix_mgr.discard_changes(discard_matrix)
    print(f"Changes pending: {discard_matrix.get_change_count()}")
    matrix_mgr.print_matrix(discard_matrix)
    
    # Example 7: Filtered matrix
    print("\n" + "=" * 80)
    print("7. FILTERED MATRIX (SPECIFIC ROLES)")
    print("=" * 80)
    
    filtered_matrix = matrix_mgr.create_matrix(
        role_ids=["role_viewer", "role_editor"],
        mode=MatrixMode.READONLY
    )
    print("\nMatrix showing only Viewer and Editor:")
    matrix_mgr.print_matrix(filtered_matrix)
    
    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80)


def setup_sample_data(rbac: RBAC):
    """Set up sample roles and permissions."""
    
    # Create permissions
    perms = [
        ("perm_doc_read", "document", "read", "Read documents"),
        ("perm_doc_write", "document", "write", "Write/edit documents"),
        ("perm_doc_delete", "document", "delete", "Delete documents"),
        ("perm_user_view", "user", "view", "View user profiles"),
        ("perm_user_manage", "user", "manage", "Manage users (create/edit/delete)"),
    ]
    
    for perm_id, resource_type, action, desc in perms:
        rbac.create_permission(
            permission_id=perm_id,
            resource_type=resource_type,
            action=action,
            description=desc
        )
    
    # Create roles
    rbac.create_role(
        role_id="role_viewer",
        name="Viewer",
        description="Can only view content",
        permissions=["perm_doc_read", "perm_user_view"]
    )
    
    rbac.create_role(
        role_id="role_editor",
        name="Editor",
        description="Can view and edit content",
        permissions=["perm_doc_read", "perm_doc_write", "perm_user_view"]
    )
    
    rbac.create_role(
        role_id="role_admin",
        name="Admin",
        description="Full system access",
        permissions=[
            "perm_doc_read", 
            "perm_doc_write", 
            "perm_doc_delete",
            "perm_user_view",
            "perm_user_manage"
        ]
    )
    
    print("Sample data created:")
    print("  Roles: Viewer, Editor, Admin")
    print("  Permissions: 5 permissions across document and user resources")


if __name__ == "__main__":
    main()
