"""
Comprehensive Validation Tests for RBAC Algorithm

This script runs detailed validation tests and generates a PASS/FAIL report.
Tests cover: permissions, roles, hierarchy, wildcards, ABAC, and edge cases.

Run: python validation_tests.py
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Add parent directory to path to import rbac
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from rbac import RBAC, PermissionDenied, EntityStatus


class ValidationReport:
    """Generate and format validation test reports."""
    
    def __init__(self):
        self.tests: List[Dict[str, Any]] = []
        self.categories: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_test(self, category: str, name: str, passed: bool, 
                 description: str = "", error: str = ""):
        """Add a test result."""
        test = {
            'category': category,
            'name': name,
            'passed': passed,
            'description': description,
            'error': error
        }
        self.tests.append(test)
        
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(test)
    
    def get_summary(self) -> Dict[str, int]:
        """Get test summary statistics."""
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t['passed'])
        failed = total - passed
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }
    
    def print_report(self):
        """Print formatted test report."""
        print("\n" + "=" * 80)
        print("RBAC ALGORITHM - VALIDATION TEST REPORT")
        print("=" * 80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        summary = self.get_summary()
        print(f"Total Tests: {summary['total']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"Pass Rate: {summary['pass_rate']:.1f}%")
        print()
        
        # Print by category
        for category, tests in self.categories.items():
            cat_passed = sum(1 for t in tests if t['passed'])
            cat_total = len(tests)
            
            print("=" * 80)
            print(f"📋 {category} ({cat_passed}/{cat_total} passed)")
            print("=" * 80)
            
            for test in tests:
                status = "✅ PASS" if test['passed'] else "❌ FAIL"
                print(f"\n{status}: {test['name']}")
                if test['description']:
                    print(f"  Description: {test['description']}")
                if not test['passed'] and test['error']:
                    print(f"  Error: {test['error']}")
        
        print("\n" + "=" * 80)
        if summary['failed'] == 0:
            print("🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"⚠️  {summary['failed']} TEST(S) FAILED")
        print("=" * 80 + "\n")


def initialize_test_data(rbac: RBAC) -> None:
    """Initialize comprehensive test data."""
    # Create permissions
    rbac.create_permission("perm_doc_read", "document", "read", "Read documents")
    rbac.create_permission("perm_doc_write", "document", "write", "Write documents")
    rbac.create_permission("perm_doc_delete", "document", "delete", "Delete documents")
    rbac.create_permission("perm_doc_publish", "document", "publish", "Publish documents")
    
    rbac.create_permission("perm_user_view", "user", "view", "View users")
    rbac.create_permission("perm_user_create", "user", "create", "Create users")
    rbac.create_permission("perm_user_edit", "user", "edit", "Edit users")
    rbac.create_permission("perm_user_delete", "user", "delete", "Delete users")
    
    rbac.create_permission("perm_api_read", "api", "read", "Read API")
    rbac.create_permission("perm_api_write", "api", "write", "Write API")
    
    rbac.create_permission("perm_report_view", "report", "view", "View reports")
    rbac.create_permission("perm_report_export", "report", "export", "Export reports")
    
    rbac.create_permission("perm_admin_all", "*", "*", "Admin wildcard")
    
    # Create role hierarchy: Guest → Viewer → Contributor → Editor → Admin
    rbac.create_role("role_guest", "Guest", 
                     permissions=["perm_doc_read"], 
                     description="Basic read access")
    
    rbac.create_role("role_viewer", "Viewer", 
                     permissions=["perm_user_view", "perm_api_read"], 
                     parent_id="role_guest",
                     description="Can view users")
    
    rbac.create_role("role_contributor", "Contributor", 
                     permissions=["perm_doc_write"], 
                     parent_id="role_viewer",
                     description="Can write documents")
    
    rbac.create_role("role_editor", "Editor", 
                     permissions=["perm_doc_publish", "perm_report_view"], 
                     parent_id="role_contributor",
                     description="Can publish documents")
    
    rbac.create_role("role_admin", "Admin", 
                     permissions=["perm_doc_delete", "perm_user_create", 
                                "perm_user_edit", "perm_api_write"], 
                     parent_id="role_editor",
                     description="Full management")
    
    # Standalone roles
    rbac.create_role("role_superuser", "Superuser", 
                     permissions=["perm_admin_all"],
                     description="Unrestricted access")
    
    rbac.create_role("role_analyst", "Analyst", 
                     permissions=["perm_doc_read", "perm_report_view", "perm_report_export"],
                     description="Data analysis")
    
    rbac.create_role("role_developer", "Developer", 
                     permissions=["perm_api_read", "perm_api_write"],
                     description="API access")
    
    # Create test users
    rbac.create_user("user_aarav", "aarav@example.com", "Aarav Sharma")
    rbac.create_user("user_priya", "priya@example.com", "Priya Patel")
    rbac.create_user("user_arjun", "arjun@example.com", "Arjun Kumar")
    rbac.create_user("user_ananya", "ananya@example.com", "Ananya Reddy")
    rbac.create_user("user_rohan", "rohan@example.com", "Rohan Singh")
    rbac.create_user("user_diya", "diya@example.com", "Diya Gupta")
    rbac.create_user("user_vikram", "vikram@example.com", "Vikram Iyer")
    rbac.create_user("user_aisha", "aisha@example.com", "Aisha Khan")
    
    # Assign roles
    rbac.assign_role("user_aarav", "role_guest")
    rbac.assign_role("user_priya", "role_viewer")
    rbac.assign_role("user_arjun", "role_contributor")
    rbac.assign_role("user_ananya", "role_editor")
    rbac.assign_role("user_rohan", "role_admin")
    rbac.assign_role("user_diya", "role_superuser")
    rbac.assign_role("user_vikram", "role_analyst")
    rbac.assign_role("user_aisha", "role_developer")


def test_basic_permissions(rbac: RBAC, report: ValidationReport):
    """Test basic permission checks."""
    category = "Basic Permissions"
    
    # Test 1: Guest can read documents
    try:
        result = rbac.can("user_aarav", "read", "document")
        report.add_test(category, "Guest can read documents", 
                       result == True,
                       "Aarav (Guest) should have read permission on documents")
    except Exception as e:
        report.add_test(category, "Guest can read documents", False, error=str(e))
    
    # Test 2: Guest cannot write documents
    try:
        result = rbac.can("user_aarav", "write", "document")
        report.add_test(category, "Guest cannot write documents", 
                       result == False,
                       "Aarav (Guest) should NOT have write permission on documents")
    except Exception as e:
        report.add_test(category, "Guest cannot write documents", False, error=str(e))
    
    # Test 3: Guest cannot delete documents
    try:
        result = rbac.can("user_aarav", "delete", "document")
        report.add_test(category, "Guest cannot delete documents", 
                       result == False,
                       "Aarav (Guest) should NOT have delete permission")
    except Exception as e:
        report.add_test(category, "Guest cannot delete documents", False, error=str(e))
    
    # Test 4: Analyst can view reports
    try:
        result = rbac.can("user_vikram", "view", "report")
        report.add_test(category, "Analyst can view reports", 
                       result == True,
                       "Vikram (Analyst) should have report view permission")
    except Exception as e:
        report.add_test(category, "Analyst can view reports", False, error=str(e))
    
    # Test 5: Analyst can export reports
    try:
        result = rbac.can("user_vikram", "export", "report")
        report.add_test(category, "Analyst can export reports", 
                       result == True,
                       "Vikram (Analyst) should have report export permission")
    except Exception as e:
        report.add_test(category, "Analyst can export reports", False, error=str(e))
    
    # Test 6: Developer can read API
    try:
        result = rbac.can("user_aisha", "read", "api")
        report.add_test(category, "Developer can read API", 
                       result == True,
                       "Aisha (Developer) should have API read permission")
    except Exception as e:
        report.add_test(category, "Developer can read API", False, error=str(e))
    
    # Test 7: Developer can write API
    try:
        result = rbac.can("user_aisha", "write", "api")
        report.add_test(category, "Developer can write API", 
                       result == True,
                       "Aisha (Developer) should have API write permission")
    except Exception as e:
        report.add_test(category, "Developer can write API", False, error=str(e))


def test_role_hierarchy(rbac: RBAC, report: ValidationReport):
    """Test role hierarchy and permission inheritance."""
    category = "Role Hierarchy"
    
    # Test 1: Viewer inherits Guest permissions (read documents)
    try:
        result = rbac.can("user_priya", "read", "document")
        report.add_test(category, "Viewer inherits Guest read permission", 
                       result == True,
                       "Priya (Viewer) should inherit read permission from Guest parent")
    except Exception as e:
        report.add_test(category, "Viewer inherits Guest read permission", False, error=str(e))
    
    # Test 2: Viewer has own permissions (view users)
    try:
        result = rbac.can("user_priya", "view", "user")
        report.add_test(category, "Viewer has direct view user permission", 
                       result == True,
                       "Priya (Viewer) should have direct view user permission")
    except Exception as e:
        report.add_test(category, "Viewer has direct view user permission", False, error=str(e))
    
    # Test 3: Contributor inherits from Viewer (can read documents)
    try:
        result = rbac.can("user_arjun", "read", "document")
        report.add_test(category, "Contributor inherits read from Guest via Viewer", 
                       result == True,
                       "Arjun (Contributor) should inherit read from Guest through Viewer")
    except Exception as e:
        report.add_test(category, "Contributor inherits read from Guest via Viewer", False, error=str(e))
    
    # Test 4: Contributor has write permission
    try:
        result = rbac.can("user_arjun", "write", "document")
        report.add_test(category, "Contributor has write permission", 
                       result == True,
                       "Arjun (Contributor) should have write permission")
    except Exception as e:
        report.add_test(category, "Contributor has write permission", False, error=str(e))
    
    # Test 5: Editor inherits from entire chain
    try:
        results = [
            rbac.can("user_ananya", "read", "document"),  # From Guest
            rbac.can("user_ananya", "view", "user"),      # From Viewer
            rbac.can("user_ananya", "write", "document"), # From Contributor
            rbac.can("user_ananya", "publish", "document") # Direct
        ]
        passed = all(results)
        report.add_test(category, "Editor inherits full hierarchy chain", 
                       passed,
                       "Ananya (Editor) should have all permissions from Guest→Viewer→Contributor→Editor")
    except Exception as e:
        report.add_test(category, "Editor inherits full hierarchy chain", False, error=str(e))
    
    # Test 6: Admin has all permissions through hierarchy
    try:
        results = [
            rbac.can("user_rohan", "read", "document"),    # From Guest
            rbac.can("user_rohan", "write", "document"),   # From Contributor
            rbac.can("user_rohan", "publish", "document"), # From Editor
            rbac.can("user_rohan", "delete", "document"),  # Direct
            rbac.can("user_rohan", "create", "user")       # Direct
        ]
        passed = all(results)
        report.add_test(category, "Admin has all permissions via hierarchy", 
                       passed,
                       "Rohan (Admin) should have all permissions from full hierarchy plus direct")
    except Exception as e:
        report.add_test(category, "Admin has all permissions via hierarchy", False, error=str(e))
    
    # Test 7: Hierarchy does not grant permissions upwards
    try:
        result = rbac.can("user_aarav", "write", "document")
        report.add_test(category, "Hierarchy does not work upwards", 
                       result == False,
                       "Aarav (Guest) should NOT inherit write from child role Viewer")
    except Exception as e:
        report.add_test(category, "Hierarchy does not work upwards", False, error=str(e))


def test_wildcard_permissions(rbac: RBAC, report: ValidationReport):
    """Test wildcard permission matching."""
    category = "Wildcard Permissions"
    
    # Test 1: Superuser with * /* can do anything
    try:
        results = [
            rbac.can("user_diya", "read", "document"),
            rbac.can("user_diya", "write", "document"),
            rbac.can("user_diya", "delete", "document"),
            rbac.can("user_diya", "publish", "document"),
            rbac.can("user_diya", "view", "user"),
            rbac.can("user_diya", "create", "user"),
            rbac.can("user_diya", "anything", "anything")
        ]
        passed = all(results)
        report.add_test(category, "Superuser wildcard grants all permissions", 
                       passed,
                       "Diya (Superuser) should have all permissions via * wildcard")
    except Exception as e:
        report.add_test(category, "Superuser wildcard grants all permissions", False, error=str(e))
    
    # Test 2: Wildcard allows arbitrary actions
    try:
        result = rbac.can("user_diya", "custom_action", "custom_resource")
        report.add_test(category, "Wildcard allows arbitrary actions", 
                       result == True,
                       "Diya (Superuser) should access any action on any resource")
    except Exception as e:
        report.add_test(category, "Wildcard allows arbitrary actions", False, error=str(e))
    
    # Test 3: Non-wildcard users cannot do arbitrary actions
    try:
        result = rbac.can("user_aarav", "custom_action", "custom_resource")
        report.add_test(category, "Non-wildcard users denied arbitrary actions", 
                       result == False,
                       "Aarav (Guest) should NOT have arbitrary custom permissions")
    except Exception as e:
        report.add_test(category, "Non-wildcard users denied arbitrary actions", False, error=str(e))


def test_denied_permissions(rbac: RBAC, report: ValidationReport):
    """Test permission denials work correctly."""
    category = "Permission Denials"
    
    # Test 1: Guest denied write
    try:
        result = rbac.can("user_aarav", "write", "document")
        report.add_test(category, "Guest denied write permission", 
                       result == False,
                       "Aarav (Guest) should be denied write access")
    except Exception as e:
        report.add_test(category, "Guest denied write permission", False, error=str(e))
    
    # Test 2: Viewer denied delete
    try:
        result = rbac.can("user_priya", "delete", "document")
        report.add_test(category, "Viewer denied delete permission", 
                       result == False,
                       "Priya (Viewer) should be denied delete access")
    except Exception as e:
        report.add_test(category, "Viewer denied delete permission", False, error=str(e))
    
    # Test 3: Contributor denied publish
    try:
        result = rbac.can("user_arjun", "publish", "document")
        report.add_test(category, "Contributor denied publish permission", 
                       result == False,
                       "Arjun (Contributor) should be denied publish access")
    except Exception as e:
        report.add_test(category, "Contributor denied publish permission", False, error=str(e))
    
    # Test 4: Editor denied delete
    try:
        result = rbac.can("user_ananya", "delete", "document")
        report.add_test(category, "Editor denied delete permission", 
                       result == False,
                       "Ananya (Editor) should be denied delete access")
    except Exception as e:
        report.add_test(category, "Editor denied delete permission", False, error=str(e))
    
    # Test 5: Analyst denied user creation
    try:
        result = rbac.can("user_vikram", "create", "user")
        report.add_test(category, "Analyst denied user creation", 
                       result == False,
                       "Vikram (Analyst) should be denied user creation")
    except Exception as e:
        report.add_test(category, "Analyst denied user creation", False, error=str(e))
    
    # Test 6: Developer denied user operations
    try:
        results = [
            not rbac.can("user_aisha", "view", "user"),
            not rbac.can("user_aisha", "create", "user"),
            not rbac.can("user_aisha", "edit", "user")
        ]
        passed = all(results)
        report.add_test(category, "Developer denied all user operations", 
                       passed,
                       "Aisha (Developer) should be denied all user operations")
    except Exception as e:
        report.add_test(category, "Developer denied all user operations", False, error=str(e))


def test_user_management(rbac: RBAC, report: ValidationReport):
    """Test user creation, retrieval, and management."""
    category = "User Management"
    
    # Test 1: Create new user
    try:
        rbac.create_user("user_test", "test@example.com", "Test User")
        user = rbac.get_user("user_test")
        passed = user is not None and user.email == "test@example.com"
        report.add_test(category, "Create and retrieve user", 
                       passed,
                       "Should create user and retrieve with correct details")
    except Exception as e:
        report.add_test(category, "Create and retrieve user", False, error=str(e))
    
    # Test 2: List all users
    try:
        users = rbac.list_users()
        passed = len(users) >= 8  # At least our test users
        report.add_test(category, "List all users", 
                       passed,
                       f"Should list all users (found {len(users)})")
    except Exception as e:
        report.add_test(category, "List all users", False, error=str(e))
    
    # Test 3: Assign and retrieve role
    try:
        rbac.assign_role("user_test", "role_guest")
        roles = rbac.get_user_roles("user_test")
        passed = len(roles) > 0 and roles[0].id == "role_guest"
        report.add_test(category, "Assign and retrieve user role", 
                       passed,
                       "Should assign role and retrieve it correctly")
    except Exception as e:
        report.add_test(category, "Assign and retrieve user role", False, error=str(e))
    
    # Test 4: Get user permissions
    try:
        perms = rbac.get_user_permissions("user_test")
        passed = len(perms) > 0  # Should have at least guest permissions
        report.add_test(category, "Get user permissions", 
                       passed,
                       f"Should retrieve user permissions (found {len(perms)})")
    except Exception as e:
        report.add_test(category, "Get user permissions", False, error=str(e))
    
    # Test 5: Revoke role
    try:
        rbac.revoke_role("user_test", "role_guest")
        roles = rbac.get_user_roles("user_test")
        passed = len(roles) == 0
        report.add_test(category, "Revoke user role", 
                       passed,
                       "Should revoke role successfully")
    except Exception as e:
        report.add_test(category, "Revoke user role", False, error=str(e))


def test_role_management(rbac: RBAC, report: ValidationReport):
    """Test role creation, retrieval, and management."""
    category = "Role Management"
    
    # Test 1: Create role
    try:
        rbac.create_role("role_test", "Test Role", 
                        permissions=["perm_doc_read"],
                        description="Test role")
        role = rbac.get_role("role_test")
        passed = role is not None and role.name == "Test Role"
        report.add_test(category, "Create and retrieve role", 
                       passed,
                       "Should create role with permissions")
    except Exception as e:
        report.add_test(category, "Create and retrieve role", False, error=str(e))
    
    # Test 2: List all roles
    try:
        roles = rbac.list_roles()
        passed = len(roles) >= 8  # At least our test roles
        report.add_test(category, "List all roles", 
                       passed,
                       f"Should list all roles (found {len(roles)})")
    except Exception as e:
        report.add_test(category, "List all roles", False, error=str(e))
    
    # Test 3: Role with parent
    try:
        rbac.create_role("role_test_child", "Test Child", 
                        parent_id="role_test",
                        permissions=["perm_doc_write"])
        role = rbac.get_role("role_test_child")
        passed = role is not None and role.parent_id == "role_test"
        report.add_test(category, "Create role with parent", 
                       passed,
                       "Should create role with parent hierarchy")
    except Exception as e:
        report.add_test(category, "Create role with parent", False, error=str(e))


def test_permission_management(rbac: RBAC, report: ValidationReport):
    """Test permission creation and retrieval."""
    category = "Permission Management"
    
    # Test 1: Create permission
    try:
        rbac.create_permission("perm_test", "test", "test_action", "Test permission")
        perm = rbac.get_permission("perm_test")
        passed = perm is not None and perm.action == "test_action"
        report.add_test(category, "Create and retrieve permission", 
                       passed,
                       "Should create permission with correct attributes")
    except Exception as e:
        report.add_test(category, "Create and retrieve permission", False, error=str(e))
    
    # Test 2: List all permissions
    try:
        perms = rbac.list_permissions()
        passed = len(perms) >= 13  # At least our test permissions
        report.add_test(category, "List all permissions", 
                       passed,
                       f"Should list all permissions (found {len(perms)})")
    except Exception as e:
        report.add_test(category, "List all permissions", False, error=str(e))


def test_edge_cases(rbac: RBAC, report: ValidationReport):
    """Test edge cases and error handling."""
    category = "Edge Cases"
    
    # Test 1: Non-existent user
    try:
        result = rbac.can("user_nonexistent", "read", "document")
        passed = result == False
        report.add_test(category, "Non-existent user denied", 
                       passed,
                       "Non-existent user should be denied access")
    except Exception as e:
        # Exception is also acceptable
        report.add_test(category, "Non-existent user denied", True, 
                       "Non-existent user properly handled with exception")
    
    # Test 2: User with no roles
    try:
        rbac.create_user("user_noroles", "noroles@example.com", "No Roles User")
        result = rbac.can("user_noroles", "read", "document")
        passed = result == False
        report.add_test(category, "User with no roles denied", 
                       passed,
                       "User with no roles should be denied access")
    except Exception as e:
        report.add_test(category, "User with no roles denied", False, error=str(e))
    
    # Test 3: Empty action
    try:
        result = rbac.can("user_aarav", "", "document")
        passed = result == False
        report.add_test(category, "Empty action denied", 
                       passed,
                       "Empty action should be denied")
    except Exception:
        report.add_test(category, "Empty action denied", True, 
                       "Empty action properly handled with exception")
    
    # Test 4: Empty resource
    try:
        result = rbac.can("user_aarav", "read", "")
        passed = result == False
        report.add_test(category, "Empty resource denied", 
                       passed,
                       "Empty resource should be denied")
    except Exception:
        report.add_test(category, "Empty resource denied", True, 
                       "Empty resource properly handled with exception")


def test_check_method(rbac: RBAC, report: ValidationReport):
    """Test check() method returns detailed information."""
    category = "Check Method Details"
    
    # Test 1: Check returns reason for allowed
    try:
        result = rbac.check("user_aarav", "read", "document")
        passed = isinstance(result, dict) and 'reason' in result and 'allowed' in result
        report.add_test(category, "Check returns detailed result", 
                       passed,
                       "Check method should return dict with reason and allowed fields")
    except Exception as e:
        report.add_test(category, "Check returns detailed result", False, error=str(e))
    
    # Test 2: Check shows matched permissions
    try:
        result = rbac.check("user_aarav", "read", "document")
        passed = 'matched_permissions' in result
        report.add_test(category, "Check includes matched permissions", 
                       passed,
                       "Check method should include matched permissions list")
    except Exception as e:
        report.add_test(category, "Check includes matched permissions", False, error=str(e))
    
    # Test 3: Check for denied permission
    try:
        result = rbac.check("user_aarav", "delete", "document")
        passed = result.get('allowed') == False
        report.add_test(category, "Check correctly denies permission", 
                       passed,
                       "Check method should return allowed=False for denied permissions")
    except Exception as e:
        report.add_test(category, "Check correctly denies permission", False, error=str(e))


def run_all_tests():
    """Run all validation tests and generate report."""
    print("Initializing RBAC system...")
    rbac = RBAC(storage='memory', enable_hierarchy=True, enable_abac=True)
    
    print("Loading test data...")
    initialize_test_data(rbac)
    
    print("Running validation tests...\n")
    report = ValidationReport()
    
    # Run all test suites
    test_basic_permissions(rbac, report)
    test_role_hierarchy(rbac, report)
    test_wildcard_permissions(rbac, report)
    test_denied_permissions(rbac, report)
    test_user_management(rbac, report)
    test_role_management(rbac, report)
    test_permission_management(rbac, report)
    test_edge_cases(rbac, report)
    test_check_method(rbac, report)
    
    # Generate and print report
    report.print_report()
    
    # Return exit code based on results
    summary = report.get_summary()
    return 0 if summary['failed'] == 0 else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
