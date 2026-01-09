"""
Permissions Matrix - Visual Role-Permission Management

This module provides a matrix-style interface for managing role-permission
assignments. It allows viewing and editing permissions in a tabular format
with roles on one axis and features/resources on the other.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import copy

from .core.models import Permission
from .core.models.role import Role
from .core.protocols import IStorageProvider
from .core.exceptions import RoleNotFound, PermissionNotFound, ValidationError


class MatrixMode(Enum):
    """Permission matrix display modes."""
    READONLY = "readonly"
    EDITABLE = "editable"


@dataclass
class PermissionCell:
    """Represents a single cell in the permissions matrix."""
    role_id: str
    permission_id: str
    granted: bool
    inherited: bool = False
    source_role: Optional[str] = None  # For inherited permissions
    can_edit: bool = True
    
    def __hash__(self):
        return hash((self.role_id, self.permission_id))


@dataclass
class MatrixRow:
    """Represents a row in the permissions matrix (a feature/resource)."""
    feature_id: str
    feature_name: str
    resource_type: str
    action: str
    description: Optional[str] = None
    cells: Dict[str, PermissionCell] = field(default_factory=dict)


@dataclass
class PermissionsMatrix:
    """
    Permissions matrix for visual role-permission management.
    
    Provides a table-like view where:
    - Rows represent features/resources (permissions)
    - Columns represent roles
    - Cells indicate whether a role has a permission (✓/✗)
    
    Example:
        ```
        Matrix View:
        
        Feature               │ Viewer │ Editor │ Admin
        ──────────────────────┼────────┼────────┼───────
        Document - Read       │   ✓    │   ✓    │   ✓
        Document - Write      │   ✗    │   ✓    │   ✓
        Document - Delete     │   ✗    │   ✗    │   ✓
        User - View           │   ✓    │   ✓    │   ✓
        User - Manage         │   ✗    │   ✗    │   ✓
        ```
    """
    roles: List[Role]
    permissions: List[Permission]
    rows: List[MatrixRow] = field(default_factory=list)
    mode: MatrixMode = MatrixMode.READONLY
    show_inherited: bool = True
    changes: Dict[Tuple[str, str], bool] = field(default_factory=dict)
    
    def has_changes(self) -> bool:
        """Check if there are any pending changes."""
        return len(self.changes) > 0
    
    def get_change_count(self) -> int:
        """Get number of pending changes."""
        return len(self.changes)


class PermissionsMatrixManager:
    """
    Manager class for creating and manipulating permissions matrices.
    
    This class provides functionality to:
    - Generate permission matrices from RBAC data
    - Toggle permissions on/off
    - Apply bulk changes
    - Export/import matrix data
    - Show permission inheritance
    
    Example:
        >>> from rbac import RBAC
        >>> from rbac.matrix import PermissionsMatrixManager
        >>> 
        >>> rbac = RBAC()
        >>> matrix_mgr = PermissionsMatrixManager(rbac._storage)
        >>> 
        >>> # Create matrix
        >>> matrix = matrix_mgr.create_matrix()
        >>> 
        >>> # Display matrix
        >>> matrix_mgr.print_matrix(matrix)
        >>> 
        >>> # Edit mode
        >>> matrix.mode = MatrixMode.EDITABLE
        >>> matrix_mgr.toggle_permission(matrix, "role_editor", "perm_doc_write")
        >>> 
        >>> # Apply changes
        >>> matrix_mgr.apply_changes(matrix)
    """
    
    def __init__(self, storage: IStorageProvider):
        """
        Initialize the matrix manager.
        
        Args:
            storage: RBAC storage provider
        """
        self._storage = storage
    
    def create_matrix(
        self,
        role_ids: Optional[List[str]] = None,
        permission_ids: Optional[List[str]] = None,
        domain: Optional[str] = None,
        mode: MatrixMode = MatrixMode.READONLY,
        show_inherited: bool = True
    ) -> PermissionsMatrix:
        """
        Create a permissions matrix.
        
        Args:
            role_ids: Optional list of role IDs to include (default: all)
            permission_ids: Optional list of permission IDs (default: all)
            domain: Optional domain filter
            mode: Matrix mode (READONLY or EDITABLE)
            show_inherited: Whether to show inherited permissions
            
        Returns:
            PermissionsMatrix object
        """
        # Get roles
        if role_ids:
            roles = [self._storage.get_role(rid) for rid in role_ids]
        else:
            roles = self._storage.list_roles(domain=domain, limit=1000)
        
        # Get permissions
        if permission_ids:
            permissions = [self._storage.get_permission(pid) for pid in permission_ids]
        else:
            permissions = self._storage.list_permissions(limit=1000)
        
        # Create matrix
        matrix = PermissionsMatrix(
            roles=roles,
            permissions=permissions,
            mode=mode,
            show_inherited=show_inherited
        )
        
        # Build rows
        matrix.rows = self._build_matrix_rows(matrix)
        
        return matrix
    
    def _build_matrix_rows(self, matrix: PermissionsMatrix) -> List[MatrixRow]:
        """Build matrix rows from permissions."""
        rows = []
        
        for perm in matrix.permissions:
            row = MatrixRow(
                feature_id=perm.id,
                feature_name=f"{perm.resource_type} - {perm.action}",
                resource_type=perm.resource_type,
                action=perm.action,
                description=perm.description
            )
            
            # Build cells for each role
            for role in matrix.roles:
                has_perm = perm.id in role.permissions
                cell = PermissionCell(
                    role_id=role.id,
                    permission_id=perm.id,
                    granted=has_perm,
                    inherited=False,
                    can_edit=matrix.mode == MatrixMode.EDITABLE
                )
                row.cells[role.id] = cell
            
            rows.append(row)
        
        return rows
    
    def toggle_permission(
        self,
        matrix: PermissionsMatrix,
        role_id: str,
        permission_id: str
    ) -> bool:
        """
        Toggle a permission for a role in the matrix.
        
        Args:
            matrix: The permissions matrix
            role_id: Role ID
            permission_id: Permission ID
            
        Returns:
            New state (True=granted, False=revoked)
            
        Raises:
            ValidationError: If matrix is not in editable mode
        """
        if matrix.mode != MatrixMode.EDITABLE:
            raise ValidationError("Matrix must be in EDITABLE mode to toggle permissions")
        
        # Find the row and cell
        for row in matrix.rows:
            if row.feature_id == permission_id:
                if role_id in row.cells:
                    cell = row.cells[role_id]
                    cell.granted = not cell.granted
                    
                    # Track change
                    key = (role_id, permission_id)
                    matrix.changes[key] = cell.granted
                    
                    return cell.granted
        
        raise ValidationError(f"Permission {permission_id} not found in matrix")
    
    def set_permission(
        self,
        matrix: PermissionsMatrix,
        role_id: str,
        permission_id: str,
        granted: bool
    ) -> None:
        """
        Set a permission state for a role.
        
        Args:
            matrix: The permissions matrix
            role_id: Role ID
            permission_id: Permission ID
            granted: Whether to grant (True) or revoke (False)
        """
        if matrix.mode != MatrixMode.EDITABLE:
            raise ValidationError("Matrix must be in EDITABLE mode to set permissions")
        
        for row in matrix.rows:
            if row.feature_id == permission_id:
                if role_id in row.cells:
                    cell = row.cells[role_id]
                    if cell.granted != granted:
                        cell.granted = granted
                        matrix.changes[(role_id, permission_id)] = granted
                    return
        
        raise ValidationError(f"Permission {permission_id} not found in matrix")
    
    def apply_changes(self, matrix: PermissionsMatrix) -> Dict[str, Any]:
        """
        Apply all pending changes to the storage.
        
        Args:
            matrix: The permissions matrix with changes
            
        Returns:
            Summary of applied changes
        """
        from dataclasses import replace
        
        if not matrix.has_changes():
            return {"success": True, "changes_applied": 0, "message": "No changes to apply"}
        
        applied = 0
        errors = []
        
        for (role_id, perm_id), granted in matrix.changes.items():
            try:
                role = self._storage.get_role(role_id)
                
                if granted:
                    # Add permission
                    if perm_id not in role.permissions:
                        new_permissions = set(role.permissions)
                        new_permissions.add(perm_id)
                        updated_role = replace(
                            role,
                            permissions=new_permissions
                        )
                        self._storage.update_role(updated_role)
                        applied += 1
                else:
                    # Remove permission
                    if perm_id in role.permissions:
                        new_permissions = set(role.permissions)
                        new_permissions.discard(perm_id)
                        updated_role = replace(
                            role,
                            permissions=new_permissions
                        )
                        self._storage.update_role(updated_role)
                        applied += 1
                        
            except Exception as e:
                errors.append(f"Error updating {role_id}/{perm_id}: {str(e)}")
        
        # Clear changes after applying
        matrix.changes.clear()
        
        return {
            "success": len(errors) == 0,
            "changes_applied": applied,
            "errors": errors
        }
    
    def discard_changes(self, matrix: PermissionsMatrix) -> None:
        """Discard all pending changes."""
        matrix.changes.clear()
        # Rebuild matrix to revert cell states
        matrix.rows = self._build_matrix_rows(matrix)
    
    def export_matrix_data(self, matrix: PermissionsMatrix) -> Dict[str, Any]:
        """
        Export matrix data as JSON-serializable dict.
        
        Returns:
            Dictionary containing matrix data
        """
        return {
            "mode": matrix.mode.value,
            "show_inherited": matrix.show_inherited,
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description
                }
                for role in matrix.roles
            ],
            "permissions": [
                {
                    "id": perm.id,
                    "resource_type": perm.resource_type,
                    "action": perm.action,
                    "description": perm.description
                }
                for perm in matrix.permissions
            ],
            "assignments": [
                {
                    "role_id": cell.role_id,
                    "permission_id": cell.permission_id,
                    "granted": cell.granted,
                    "inherited": cell.inherited
                }
                for row in matrix.rows
                for cell in row.cells.values()
                if cell.granted
            ]
        }
    
    def print_matrix(
        self,
        matrix: PermissionsMatrix,
        show_descriptions: bool = False,
        max_role_name_len: int = 15
    ) -> None:
        """
        Print matrix in a formatted table.
        
        Args:
            matrix: The permissions matrix
            show_descriptions: Whether to show permission descriptions
            max_role_name_len: Maximum length for role names (truncate if longer)
        """
        import sys
        
        if not matrix.rows:
            print("Empty matrix - no permissions or roles found")
            return
        
        # Check if we can use Unicode characters
        try:
            # Try to encode Unicode characters
            "│".encode(sys.stdout.encoding or 'utf-8')
            vertical_bar = "│"
            horizontal_bar = "─"
            check_mark = "✓"
            cross_mark = "✗"
            up_arrow = "⇑"
            warning = "⚠"
            bulb = "💡"
        except (UnicodeEncodeError, LookupError, AttributeError):
            # Fall back to ASCII characters
            vertical_bar = "|"
            horizontal_bar = "-"
            check_mark = "Y"
            cross_mark = "N"
            up_arrow = "^"
            warning = "!"
            bulb = "*"
        
        # Header
        role_names = [r.name[:max_role_name_len] for r in matrix.roles]
        feature_col_width = max(30, max(len(row.feature_name) for row in matrix.rows))
        
        # Print header
        header = f"{'Feature':<{feature_col_width}}"
        for name in role_names:
            header += f" {vertical_bar} {name:^{max_role_name_len}}"
        print(header)
        print(horizontal_bar * len(header))
        
        # Print rows
        for row in matrix.rows:
            line = f"{row.feature_name:<{feature_col_width}}"
            for role in matrix.roles:
                cell = row.cells.get(role.id)
                if cell:
                    symbol = check_mark if cell.granted else cross_mark
                    if cell.inherited and matrix.show_inherited:
                        symbol = up_arrow if cell.granted else cross_mark
                    line += f" {vertical_bar} {symbol:^{max_role_name_len}}"
                else:
                    line += f" {vertical_bar} {'-':^{max_role_name_len}}"
            print(line)
            
            if show_descriptions and row.description:
                print(f"  -> {row.description}")
        
        # Footer
        if matrix.has_changes():
            print(f"\n{warning} {matrix.get_change_count()} pending changes (call apply_changes() to save)")
        
        print(f"\nMode: {matrix.mode.value}")
        if matrix.mode == MatrixMode.EDITABLE:
            print(f"{bulb} Use toggle_permission() or set_permission() to edit")
