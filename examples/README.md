# RBAC Examples

This directory contains comprehensive examples demonstrating the features and capabilities of the RBAC Algorithm library.

## Prerequisites

Make sure the RBAC package is installed:

```bash
# From the repository root
pip install -e .
```

## Available Examples

### 1. Basic Usage (`basic_usage.py`) ✅

Demonstrates core RBAC features:
- Creating users, roles, and permissions
- Role hierarchy (inheritance)
- Assigning roles to users
- Simple permission checks
- Temporary role assignments

**Run:**
```bash
python examples/basic_usage.py
```

**What you'll learn:**
- How to initialize RBAC
- Creating permissions for different actions
- Setting up role hierarchies (Viewer → Editor → Admin)
- Checking if users can perform actions
- Granting temporary admin access

---

### 2. Advanced ABAC (`abac_example.py`) ✅

Demonstrates Attribute-Based Access Control:
- Conditional permissions based on attributes
- Resource ownership checks
- Department-based access
- Time-based policies
- Level-based authorization

**Run:**
```bash
python examples/abac_example.py
```

**What you'll learn:**
- Creating permissions with ABAC conditions
- Using template variables like `{{user.id}}`
- Attribute matching (`user.department == resource.department`)
- Numeric comparisons (`user.level > 5`)
- Time-based conditions (business hours)
- Multiple condition logic (AND)

**Key Concepts:**
```python
# Permission with ownership check
conditions={
    "resource.owner_id": {"==": "{{user.id}}"}
}

# Permission with department matching
conditions={
    "resource.department": {"==": "{{user.department}}"}
}

# Permission with time restriction
conditions={
    "time.hour": {">": 8, "<": 18},
    "user.level": {">": 5}
}
```

---

### 3. Permissions Matrix (`permissions_matrix_example.py`) ✅ *NEW!*

Demonstrates visual role-permission management:
- Creating read-only and editable matrices
- Toggling and setting permissions
- Applying/discarding changes
- Bulk permission operations
- Exporting matrix data
- Filtering by roles or permissions

**Run:**
```bash
python examples/permissions_matrix_example.py
```

**What you'll learn:**
- Creating permission matrices (READONLY vs EDITABLE modes)
- Visual table display of role×permission assignments
- Interactive permission editing with change tracking
- Applying changes to storage atomically
- Discarding pending changes
- Exporting matrix data for auditing
- Filtering matrices for specific roles/permissions

**Sample Output:**
```
Feature                    |     Viewer      |     Editor      |      Admin
-------------------------------------------------------------------------------
document - read            |        Y        |        Y        |        Y
document - write           |        N        |        Y        |        Y
document - delete          |        N        |        N        |        Y

! 3 pending changes (call apply_changes() to save)
```

**Key Features:**
- **Two Modes**: READONLY (safe viewing) and EDITABLE (modifications)
- **Change Tracking**: All modifications tracked before applying
- **Bulk Operations**: Modify multiple permissions at once
- **Export**: JSON serialization for reporting
- **Pretty Display**: Formatted tables with ✓/✗ or Y/N symbols

---

## Planned Examples

### 4. Multi-Tenancy (`multi_tenancy_example.py`) 📋

Will demonstrate tenant isolation and cross-tenant access control.

---

### 5. Performance Benchmarks (`benchmark.py`) 📋

Will demonstrate performance testing and optimization strategies.

---

## Example Scenarios

### Scenario 1: Document Management System

**Use Case:** A document management system where users can read, write, and delete documents based on their role and ownership.

**Permissions:**
- `read` - View documents
- `write` - Edit documents
- `delete` - Remove documents

**Roles:**
- **Viewer** - Can only read
- **Editor** - Can read and write (inherits from Viewer)
- **Admin** - Full access (inherits from Editor)

**ABAC Rules:**
- Users can only edit their own documents
- Managers can read all documents in their department
- Delete requires level > 5 AND status = 'draft'

**See:** `basic_usage.py` and `abac_example.py`

---

### Scenario 2: Healthcare System

**Use Case:** Hospital system with patient records requiring HIPAA compliance.

**Permissions:**
- `view_patient` - View patient records
- `edit_patient` - Update patient records
- `view_medical_history` - Access medical history
- `prescribe` - Write prescriptions

**Roles:**
- **Nurse** - View and update basic patient info
- **Doctor** - Full medical access including prescriptions
- **Specialist** - Limited to their specialty
- **Admin** - System administration

**ABAC Rules:**
- Doctors can only access patients in their department
- Nurses can only access assigned patients
- All access logged for HIPAA compliance
- Emergency override for critical situations

**Implementation:** See `healthcare_example.py` *(Coming Soon)*

---

### Scenario 3: E-Commerce Platform

**Use Case:** Multi-tenant e-commerce with vendors and customers.

**Permissions:**
- `view_products` - Browse products
- `manage_products` - Add/edit products
- `view_orders` - View orders
- `process_orders` - Fulfill orders
- `view_analytics` - Access reports

**Roles:**
- **Customer** - View products, place orders
- **Vendor** - Manage own products and orders
- **Support** - View orders, assist customers
- **Platform Admin** - Full platform access

**ABAC Rules:**
- Vendors can only manage their own products
- Support can only access orders they're assigned to
- Analytics limited by domain/tenant
- Customers can only view their own orders

**Implementation:** See `ecommerce_example.py` *(Coming Soon)*

---

## Testing Your Integration

### Quick Start Template

```python
from rbac import RBAC

# Initialize
rbac = RBAC(storage='memory')

# Create permission
permission = rbac.create_permission(
    permission_id="perm_resource_action",
    resource_type="resource_name",
    action="action_name",
    conditions=None  # or ABAC conditions dict
)

# Create role
role = rbac.create_role(
    role_id="role_name",
    name="Display Name",
    permissions=["perm_resource_action"]
)

# Create user
user = rbac.create_user(
    user_id="user_123",
    email="user@example.com",
    name="User Name",
    attributes={"custom": "attributes"}
)

# Assign role
rbac.assign_role("user_123", "role_name")

# Check permission
if rbac.can("user_123", "action_name", "resource_name"):
    # Grant access
    pass
else:
    # Deny access
    pass
```

---

## Common Patterns

### Pattern 1: Role Hierarchy

```python
# Create base role
viewer = rbac.create_role(
    role_id="role_viewer",
    name="Viewer",
    permissions=["perm_read"]
)

# Create child role (inherits from viewer)
editor = rbac.create_role(
    role_id="role_editor",
    name="Editor",
    permissions=["perm_read", "perm_write"],
    parent_id="role_viewer"
)
```

**Result:** Editors automatically get all Viewer permissions plus their own.

---

### Pattern 2: Ownership-Based Access

```python
# Permission that checks ownership
permission = rbac.create_permission(
    permission_id="perm_edit_own",
    resource_type="document",
    action="write",
    conditions={
        "resource.owner_id": {"==": "{{user.id}}"}
    }
)
```

**Result:** Users can only edit resources they own.

---

### Pattern 3: Department-Based Access

```python
# Permission for department members
permission = rbac.create_permission(
    permission_id="perm_read_dept",
    resource_type="document",
    action="read",
    conditions={
        "resource.department": {"==": "{{user.department}}"}
    }
)
```

**Result:** Users can only access resources in their department.

---

### Pattern 4: Level-Based Access

```python
# Permission requiring minimum level
permission = rbac.create_permission(
    permission_id="perm_admin_action",
    resource_type="system",
    action="configure",
    conditions={
        "user.level": {">": 8}
    }
)
```

**Result:** Only users with level > 8 can perform action.

---

### Pattern 5: Time-Based Access

```python
# Permission limited to business hours
permission = rbac.create_permission(
    permission_id="perm_business_hours",
    resource_type="document",
    action="delete",
    conditions={
        "time.hour": {">": 8, "<": 18}
    }
)
```

**Result:** Action only allowed during business hours.

---

## Troubleshooting

### Issue: "User not found"
**Cause:** User ID doesn't start with "user_"
**Solution:** Ensure user IDs follow format: `user_<identifier>`

### Issue: "Permission denied"
**Cause:** User lacks required permission or ABAC condition failed
**Solution:** Use `rbac.check()` to get detailed reason

### Issue: "Circular dependency"
**Cause:** Role hierarchy has a cycle
**Solution:** Check parent_id values don't create loops

### Issue: "ABAC condition always fails"
**Cause:** Template variable not found in context or wrong attribute path
**Solution:** Verify attribute paths and ensure resources have required attributes

---

## Next Steps

1. **Read the Protocol Specification:** [PROTOCOL.md](../PROTOCOL.md)
2. **Review Core Architecture:** [ARCHITECTURE.md](../ARCHITECTURE.md)
3. **Implement Language Adapters:** [ADAPTERS.md](../ADAPTERS.md)
4. **Contribute:** [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Support

- **Documentation:** [docs/](../docs/)
- **Issues:** [GitHub Issues](https://github.com/rbac-algorithm/issues)
- **Discussions:** [GitHub Discussions](https://github.com/rbac-algorithm/discussions)
