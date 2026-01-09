# Permissions Matrix

The Permissions Matrix feature provides a visual, tabular interface for managing role-permission assignments. It displays roles as columns and permissions as rows, making it easy to see and modify which roles have which permissions.

## Features

- **Visual Table Layout**: Clear matrix view with roles × permissions
- **Two Modes**: 
  - `READONLY`: Safe viewing without modifications
  - `EDITABLE`: Interactive permission management
- **Change Tracking**: All modifications tracked before applying
- **Bulk Operations**: Modify multiple permissions at once
- **Export/Import**: JSON serialization for data portability
- **Formatted Display**: Pretty-printed tables with Unicode/ASCII fallback

## Quick Start

```python
from rbac import RBAC, PermissionsMatrixManager, MatrixMode

# Setup
rbac = RBAC()
storage = rbac._storage
matrix_mgr = PermissionsMatrixManager(storage)

# Create a read-only matrix
matrix = matrix_mgr.create_matrix(mode=MatrixMode.READONLY)
matrix_mgr.print_matrix(matrix)

# Create an editable matrix
editable_matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)

# Toggle permission
matrix_mgr.toggle_permission(editable_matrix, "role_viewer", "perm_write")

# Set specific state
matrix_mgr.set_permission(editable_matrix, "role_admin", "perm_delete", True)

# Apply changes to storage
result = matrix_mgr.apply_changes(editable_matrix)
print(f"Applied {result['changes_applied']} changes")
```

## API Reference

### PermissionsMatrixManager

Main class for managing permissions matrices.

#### Constructor

```python
matrix_mgr = PermissionsMatrixManager(storage: IStorageProvider)
```

#### Methods

##### create_matrix()

Create a new permissions matrix.

```python
matrix = matrix_mgr.create_matrix(
    role_ids: Optional[List[str]] = None,
    permission_ids: Optional[List[str]] = None,
    domain: Optional[str] = None,
    mode: MatrixMode = MatrixMode.READONLY,
    show_inherited: bool = False
)
```

**Parameters:**
- `role_ids`: Specific roles to include (None = all roles)
- `permission_ids`: Specific permissions to include (None = all permissions)
- `domain`: Domain filter for multi-tenancy
- `mode`: `READONLY` or `EDITABLE`
- `show_inherited`: Display inherited permissions

**Returns:** `PermissionsMatrix` object

##### toggle_permission()

Toggle a permission's state for a role.

```python
changed = matrix_mgr.toggle_permission(
    matrix: PermissionsMatrix,
    role_id: str,
    permission_id: str
) -> bool
```

**Returns:** `True` if state changed, `False` if no change

**Raises:** `ValidationError` if matrix is in READONLY mode

##### set_permission()

Set a permission to a specific state.

```python
matrix_mgr.set_permission(
    matrix: PermissionsMatrix,
    role_id: str,
    permission_id: str,
    granted: bool
)
```

**Parameters:**
- `granted`: `True` to grant permission, `False` to revoke

**Raises:** `ValidationError` if matrix is in READONLY mode

##### apply_changes()

Apply all pending changes to storage.

```python
result = matrix_mgr.apply_changes(matrix: PermissionsMatrix) -> Dict[str, Any]
```

**Returns:** Dictionary with:
```python
{
    "success": bool,           # All changes applied successfully
    "changes_applied": int,    # Number of changes applied
    "errors": List[str]        # Error messages if any
}
```

##### discard_changes()

Discard all pending changes and revert to storage state.

```python
matrix_mgr.discard_changes(matrix: PermissionsMatrix)
```

##### export_matrix_data()

Export matrix data as JSON-serializable dictionary.

```python
data = matrix_mgr.export_matrix_data(matrix: PermissionsMatrix) -> Dict[str, Any]
```

**Returns:** Dictionary containing roles, permissions, and assignments

##### print_matrix()

Print formatted matrix table to console.

```python
matrix_mgr.print_matrix(
    matrix: PermissionsMatrix,
    show_descriptions: bool = False,
    max_role_name_len: int = 15
)
```

**Parameters:**
- `show_descriptions`: Include permission descriptions
- `max_role_name_len`: Maximum column width for role names

### PermissionsMatrix

Data structure representing the permissions matrix.

**Attributes:**
- `roles`: List of Role objects
- `permissions`: List of Permission objects
- `rows`: List of MatrixRow objects
- `mode`: `READONLY` or `EDITABLE`
- `show_inherited`: Whether to display inherited permissions
- `changes`: Dictionary tracking pending changes

**Methods:**
- `has_changes() -> bool`: Check if there are pending changes
- `get_change_count() -> int`: Get number of pending changes

## Usage Examples

### Example 1: View Current Permissions

```python
# Create read-only matrix
matrix = matrix_mgr.create_matrix(mode=MatrixMode.READONLY)

# Display as table
matrix_mgr.print_matrix(matrix)

# Output:
# Feature                        |     Viewer      |     Editor      |      Admin
# ------------------------------------------------------------------------------------
# document - read                |        Y        |        Y        |        Y
# document - write               |        N        |        Y        |        Y
# document - delete              |        N        |        N        |        Y
```

### Example 2: Make Changes

```python
# Create editable matrix
matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)

# Grant document write to Viewer
matrix_mgr.set_permission(matrix, "role_viewer", "perm_doc_write", True)

# Toggle document delete for Admin
matrix_mgr.toggle_permission(matrix, "role_admin", "perm_doc_delete")

# Check pending changes
print(f"{matrix.get_change_count()} changes pending")

# Apply to storage
result = matrix_mgr.apply_changes(matrix)
if result["success"]:
    print(f"Applied {result['changes_applied']} changes")
else:
    print(f"Errors: {result['errors']}")
```

### Example 3: Bulk Operations

```python
matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)

# Grant all document permissions to Admin
for perm in matrix.permissions:
    if perm.resource_type == "document":
        matrix_mgr.set_permission(matrix, "role_admin", perm.id, True)

# Revoke all user permissions from Viewer
for perm in matrix.permissions:
    if perm.resource_type == "user":
        matrix_mgr.set_permission(matrix, "role_viewer", perm.id, False)

# Apply all changes at once
result = matrix_mgr.apply_changes(matrix)
```

### Example 4: Filtered Matrix

```python
# Show only specific roles
viewer_editor_matrix = matrix_mgr.create_matrix(
    role_ids=["role_viewer", "role_editor"]
)
matrix_mgr.print_matrix(viewer_editor_matrix)

# Show only specific permissions
doc_perms = [p.id for p in storage.list_permissions() if p.resource_type == "document"]
doc_matrix = matrix_mgr.create_matrix(permission_ids=doc_perms)
matrix_mgr.print_matrix(doc_matrix)
```

### Example 5: Export and Audit

```python
# Export current state
data = matrix_mgr.export_matrix_data(matrix)

# Analyze assignments
print(f"Total roles: {len(data['roles'])}")
print(f"Total permissions: {len(data['permissions'])}")
print(f"Active assignments: {len(data['assignments'])}")

# List all role-permission pairs
for assignment in data['assignments']:
    role_name = assignment['role_name']
    perm = assignment['permission']
    print(f"{role_name} -> {perm['resource_type']}.{perm['action']}")
```

### Example 6: Change Tracking

```python
matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)

# Make several changes
matrix_mgr.toggle_permission(matrix, "role_viewer", "perm_write")
matrix_mgr.toggle_permission(matrix, "role_editor", "perm_delete")
matrix_mgr.set_permission(matrix, "role_admin", "perm_special", True)

# Review changes
print(f"{matrix.get_change_count()} changes pending:")
matrix_mgr.print_matrix(matrix)  # Shows pending indicator

# Decide to discard
matrix_mgr.discard_changes(matrix)
print("Changes discarded")
```

## Matrix Display

The matrix uses a table format with:

- **Columns**: Roles (can be filtered)
- **Rows**: Permissions (feature name = resource_type - action)
- **Cells**: Y (granted), N (not granted), ^ (inherited)
- **Footer**: Shows pending changes count and mode

### Unicode vs ASCII Display

The display automatically detects terminal encoding:

**Unicode** (UTF-8 terminals):
```
Feature                        │     Viewer      │     Editor      │      Admin
────────────────────────────────────────────────────────────────────────────────
document - read                │        ✓        │        ✓        │        ✓
document - write               │        ✗        │        ✓        │        ✓
```

**ASCII** (Windows console, limited encoding):
```
Feature                        |     Viewer      |     Editor      |      Admin
------------------------------------------------------------------------------------
document - read                |        Y        |        Y        |        Y
document - write               |        N        |        Y        |        Y
```

## Change Workflow

The matrix supports a transactional workflow:

1. **Create editable matrix** - Enter editing mode
2. **Make changes** - Toggle/set permissions as needed
3. **Review changes** - Check pending changes count and display
4. **Decide**:
   - **Apply** - Persist changes to storage
   - **Discard** - Revert to storage state
5. **Verify** - Create new matrix to confirm changes

This workflow prevents accidental modifications and allows bulk changes to be applied atomically.

## Error Handling

```python
from rbac import ValidationError

try:
    # Attempt to modify read-only matrix
    readonly_matrix = matrix_mgr.create_matrix(mode=MatrixMode.READONLY)
    matrix_mgr.toggle_permission(readonly_matrix, "role_admin", "perm_write")
except ValidationError as e:
    print(f"Error: {e}")  # "Matrix must be in EDITABLE mode"

# Apply changes with error checking
result = matrix_mgr.apply_changes(matrix)
if not result["success"]:
    for error in result["errors"]:
        print(f"Failed: {error}")
```

## Integration with RBAC

The permissions matrix integrates seamlessly with the RBAC system:

```python
# Standard RBAC operations
rbac = RBAC()
rbac.create_role("role_admin", "Administrator")
rbac.create_permission("perm_write", "document", "write")

# Matrix operations use same storage
matrix_mgr = PermissionsMatrixManager(rbac._storage)
matrix = matrix_mgr.create_matrix()

# Changes in matrix reflect in RBAC
matrix_mgr.set_permission(matrix, "role_admin", "perm_write", True)
matrix_mgr.apply_changes(matrix)

# Verify with RBAC
admin_role = rbac._storage.get_role("role_admin")
assert "perm_write" in admin_role.permissions  # True
```

## Best Practices

1. **Use READONLY for viewing** - Prevent accidental modifications
2. **Review before applying** - Check `get_change_count()` and display matrix
3. **Handle errors** - Check `result["success"]` after applying
4. **Filter for performance** - Use `role_ids`/`permission_ids` for large systems
5. **Export for auditing** - Use `export_matrix_data()` for compliance reports
6. **Batch changes** - Make multiple edits before applying to reduce transactions

## See Also

- [Role Management](../api/roles.md)
- [Permission Management](../api/permissions.md)
- [Multi-tenancy](multi-tenancy.md)
- [Examples](../../examples/permissions_matrix_example.py)
