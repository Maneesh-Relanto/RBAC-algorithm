"""
Unit tests for Permissions Matrix functionality.
"""

import pytest
from rbac import RBAC, ValidationError
from rbac.matrix import (
    PermissionsMatrixManager, MatrixMode, PermissionCell,
    MatrixRow, PermissionsMatrix
)


class TestPermissionsMatrix:
    """Test cases for permissions matrix operations."""
    
    @pytest.fixture
    def rbac_with_data(self):
        """Create RBAC instance with sample data."""
        rbac = RBAC(storage='memory')
        
        # Create permissions
        rbac.create_permission("perm_doc_read", "document", "read")
        rbac.create_permission("perm_doc_write", "document", "write")
        rbac.create_permission("perm_doc_delete", "document", "delete")
        
        # Create roles
        rbac.create_role("role_viewer", "Viewer", permissions=["perm_doc_read"])
        rbac.create_role("role_editor", "Editor", permissions=["perm_doc_read", "perm_doc_write"])
        rbac.create_role("role_admin", "Admin", permissions=["perm_doc_read", "perm_doc_write", "perm_doc_delete"])
        
        return rbac
    
    @pytest.fixture
    def matrix_manager(self, rbac_with_data):
        """Create matrix manager."""
        return PermissionsMatrixManager(rbac_with_data._storage)
    
    def test_create_readonly_matrix(self, matrix_manager):
        """Test creating a read-only matrix."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.READONLY)
        
        assert matrix is not None
        assert len(matrix.roles) == 3
        assert len(matrix.permissions) == 3
        assert len(matrix.rows) == 3
        assert matrix.mode == MatrixMode.READONLY
    
    def test_create_editable_matrix(self, matrix_manager):
        """Test creating an editable matrix."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.EDITABLE)
        
        assert matrix.mode == MatrixMode.EDITABLE
        
        # Check that cells are editable
        for row in matrix.rows:
            for cell in row.cells.values():
                assert cell.can_edit is True
    
    def test_matrix_structure(self, matrix_manager):
        """Test matrix structure is correct."""
        matrix = matrix_manager.create_matrix()
        
        # Check rows
        assert len(matrix.rows) == 3  # 3 permissions
        
        # Check each row has cells for all roles
        for row in matrix.rows:
            assert len(row.cells) == 3  # 3 roles
            assert "role_viewer" in row.cells
            assert "role_editor" in row.cells
            assert "role_admin" in row.cells
    
    def test_permission_states(self, matrix_manager):
        """Test that permission states are correctly reflected."""
        matrix = matrix_manager.create_matrix()
        
        # Find perm_doc_read row
        doc_read_row = next(r for r in matrix.rows if r.feature_id == "perm_doc_read")
        
        # All roles should have doc_read
        assert doc_read_row.cells["role_viewer"].granted is True
        assert doc_read_row.cells["role_editor"].granted is True
        assert doc_read_row.cells["role_admin"].granted is True
        
        # Find perm_doc_delete row
        doc_delete_row = next(r for r in matrix.rows if r.feature_id == "perm_doc_delete")
        
        # Only admin should have doc_delete
        assert doc_delete_row.cells["role_viewer"].granted is False
        assert doc_delete_row.cells["role_editor"].granted is False
        assert doc_delete_row.cells["role_admin"].granted is True
    
    def test_toggle_permission(self, matrix_manager):
        """Test toggling a permission."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.EDITABLE)
        
        # Toggle perm_doc_write for role_viewer (should grant it)
        result = matrix_manager.toggle_permission(matrix, "role_viewer", "perm_doc_write")
        
        assert result is True  # Now granted
        assert matrix.has_changes() is True
        assert matrix.get_change_count() == 1
        
        # Toggle again (should revoke it)
        result = matrix_manager.toggle_permission(matrix, "role_viewer", "perm_doc_write")
        
        assert result is False  # Now revoked
        # Should have 2 changes (grant then revoke)
        assert matrix.get_change_count() == 1  # Net change is still 1
    
    def test_toggle_permission_readonly_error(self, matrix_manager):
        """Test that toggling in readonly mode raises error."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.READONLY)
        
        with pytest.raises(ValidationError, match="EDITABLE mode"):
            matrix_manager.toggle_permission(matrix, "role_viewer", "perm_doc_write")
    
    def test_set_permission(self, matrix_manager):
        """Test setting a specific permission state."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.EDITABLE)
        
        # Grant permission
        matrix_manager.set_permission(matrix, "role_viewer", "perm_doc_write", True)
        
        assert matrix.has_changes() is True
        assert ("role_viewer", "perm_doc_write") in matrix.changes
        assert matrix.changes[("role_viewer", "perm_doc_write")] is True
        
        # Revoke permission
        matrix_manager.set_permission(matrix, "role_admin", "perm_doc_delete", False)
        
        assert matrix.get_change_count() == 2
    
    def test_apply_changes(self, matrix_manager, rbac_with_data):
        """Test applying changes to storage."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.EDITABLE)
        
        # Grant perm_doc_write to role_viewer
        matrix_manager.set_permission(matrix, "role_viewer", "perm_doc_write", True)
        
        # Apply changes
        result = matrix_manager.apply_changes(matrix)
        
        assert result["success"] is True
        assert result["changes_applied"] == 1
        assert len(result["errors"]) == 0
        assert matrix.has_changes() is False
        
        # Verify in storage
        viewer_role = rbac_with_data._storage.get_role("role_viewer")
        assert "perm_doc_write" in viewer_role.permissions
    
    def test_discard_changes(self, matrix_manager):
        """Test discarding changes."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.EDITABLE)
        
        # Make changes
        matrix_manager.toggle_permission(matrix, "role_viewer", "perm_doc_write")
        matrix_manager.toggle_permission(matrix, "role_editor", "perm_doc_delete")
        
        assert matrix.get_change_count() == 2
        
        # Discard
        matrix_manager.discard_changes(matrix)
        
        assert matrix.has_changes() is False
        assert matrix.get_change_count() == 0
    
    def test_export_matrix_data(self, matrix_manager):
        """Test exporting matrix data."""
        matrix = matrix_manager.create_matrix()
        
        data = matrix_manager.export_matrix_data(matrix)
        
        assert "roles" in data
        assert "permissions" in data
        assert "assignments" in data
        
        assert len(data["roles"]) == 3
        assert len(data["permissions"]) == 3
        assert len(data["assignments"]) > 0
        
        # Check structure
        assert "id" in data["roles"][0]
        assert "name" in data["roles"][0]
        assert "resource_type" in data["permissions"][0]
        assert "action" in data["permissions"][0]
    
    def test_filtered_matrix_by_roles(self, matrix_manager):
        """Test creating filtered matrix with specific roles."""
        matrix = matrix_manager.create_matrix(
            role_ids=["role_viewer", "role_editor"]
        )
        
        assert len(matrix.roles) == 2
        assert len(matrix.permissions) == 3  # All permissions
        
        # Each row should only have 2 cells
        for row in matrix.rows:
            assert len(row.cells) == 2
    
    def test_filtered_matrix_by_permissions(self, matrix_manager):
        """Test creating filtered matrix with specific permissions."""
        matrix = matrix_manager.create_matrix(
            permission_ids=["perm_doc_read", "perm_doc_write"]
        )
        
        assert len(matrix.roles) == 3  # All roles
        assert len(matrix.permissions) == 2  # Filtered permissions
        assert len(matrix.rows) == 2
    
    def test_multiple_changes_apply(self, matrix_manager, rbac_with_data):
        """Test applying multiple changes at once."""
        matrix = matrix_manager.create_matrix(mode=MatrixMode.EDITABLE)
        
        # Make multiple changes
        matrix_manager.set_permission(matrix, "role_viewer", "perm_doc_write", True)
        matrix_manager.set_permission(matrix, "role_viewer", "perm_doc_delete", True)
        matrix_manager.set_permission(matrix, "role_admin", "perm_doc_delete", False)
        
        assert matrix.get_change_count() == 3
        
        # Apply all
        result = matrix_manager.apply_changes(matrix)
        
        assert result["success"] is True
        assert result["changes_applied"] == 3
        
        # Verify
        viewer = rbac_with_data._storage.get_role("role_viewer")
        admin = rbac_with_data._storage.get_role("role_admin")
        
        assert "perm_doc_write" in viewer.permissions
        assert "perm_doc_delete" in viewer.permissions
        assert "perm_doc_delete" not in admin.permissions
    
    def test_matrix_row_structure(self, matrix_manager):
        """Test matrix row structure."""
        matrix = matrix_manager.create_matrix()
        
        row = matrix.rows[0]
        
        assert isinstance(row, MatrixRow)
        assert row.feature_id is not None
        assert row.feature_name is not None
        assert row.resource_type is not None
        assert row.action is not None
        assert isinstance(row.cells, dict)
    
    def test_permission_cell_structure(self, matrix_manager):
        """Test permission cell structure."""
        matrix = matrix_manager.create_matrix()
        
        cell = matrix.rows[0].cells["role_viewer"]
        
        assert isinstance(cell, PermissionCell)
        assert cell.role_id == "role_viewer"
        assert cell.permission_id is not None
        assert isinstance(cell.granted, bool)
        assert isinstance(cell.inherited, bool)


class TestMatrixPrinting:
    """Test matrix printing functionality."""
    
    @pytest.fixture
    def rbac_with_data(self):
        """Create RBAC with sample data."""
        rbac = RBAC(storage='memory')
        rbac.create_permission("perm_doc_read", "document", "read")
        rbac.create_role("role_viewer", "Viewer", permissions=["perm_doc_read"])
        return rbac
    
    def test_print_matrix_doesnt_crash(self, rbac_with_data, capsys):
        """Test that print_matrix doesn't crash."""
        manager = PermissionsMatrixManager(rbac_with_data._storage)
        matrix = manager.create_matrix()
        
        # Should not raise exception
        manager.print_matrix(matrix)
        
        captured = capsys.readouterr()
        assert "Feature" in captured.out
        assert "Viewer" in captured.out
    
    def test_print_empty_matrix(self, capsys):
        """Test printing empty matrix."""
        rbac = RBAC(storage='memory')
        manager = PermissionsMatrixManager(rbac._storage)
        
        matrix = manager.create_matrix()
        manager.print_matrix(matrix)
        
        captured = capsys.readouterr()
        assert "Empty matrix" in captured.out
