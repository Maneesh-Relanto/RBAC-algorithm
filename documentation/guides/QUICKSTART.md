# Quick Start Guide

Get started with RBAC Algorithm in 5 minutes!

## Installation

```bash
pip install rbac-algorithm
```

Or from source:

```bash
git clone https://github.com/rbac-algorithm/rbac-python.git
cd rbac-python
pip install -e .
```

## Your First RBAC System

### Step 1: Initialize RBAC

```python
from rbac import RBAC

# Create an RBAC instance with in-memory storage
rbac = RBAC(storage='memory')
```

### Step 2: Create Permissions

```python
# Define what actions can be performed
read_perm = rbac.create_permission(
    permission_id="perm_doc_read",
    resource_type="document",
    action="read",
    description="Can read documents"
)

write_perm = rbac.create_permission(
    permission_id="perm_doc_write",
    resource_type="document",
    action="write",
    description="Can write/edit documents"
)

delete_perm = rbac.create_permission(
    permission_id="perm_doc_delete",
    resource_type="document",
    action="delete",
    description="Can delete documents"
)
```

### Step 3: Create Roles

```python
# Create roles with different permission sets
viewer = rbac.create_role(
    role_id="role_viewer",
    name="Viewer",
    permissions=["perm_doc_read"]
)

editor = rbac.create_role(
    role_id="role_editor",
    name="Editor",
    permissions=["perm_doc_read", "perm_doc_write"],
    parent_id="role_viewer"  # Inherits from Viewer
)

admin = rbac.create_role(
    role_id="role_admin",
    name="Admin",
    permissions=["perm_doc_read", "perm_doc_write", "perm_doc_delete"],
    parent_id="role_editor"  # Inherits from Editor
)
```

### Step 4: Create Users

```python
# Create users
alice = rbac.create_user(
    user_id="user_alice",
    email="alice@example.com",
    name="Alice Johnson"
)

bob = rbac.create_user(
    user_id="user_bob",
    email="bob@example.com",
    name="Bob Smith"
)
```

### Step 5: Assign Roles

```python
# Assign roles to users
rbac.assign_role("user_alice", "role_viewer")
rbac.assign_role("user_bob", "role_editor")
```

### Step 6: Check Permissions

```python
# Check if a user can perform an action
if rbac.can("user_alice", "read", "document"):
    print("Alice can read documents!")
    
if rbac.can("user_alice", "write", "document"):
    print("Alice can write documents!")
else:
    print("Alice cannot write documents")

# Bob (editor) can both read and write
if rbac.can("user_bob", "write", "document"):
    print("Bob can write documents!")
```

### Step 7: Enforce Permissions (Optional)

```python
from rbac import PermissionDenied

try:
    # This will raise PermissionDenied if Alice can't delete
    rbac.require("user_alice", "delete", "document")
    delete_document()
except PermissionDenied as e:
    print(f"Access denied: {e}")
```

## Complete Example

```python
from rbac import RBAC

# Initialize
rbac = RBAC(storage='memory')

# Setup permissions
rbac.create_permission("perm_read", "document", "read")
rbac.create_permission("perm_write", "document", "write")
rbac.create_permission("perm_delete", "document", "delete")

# Setup roles with hierarchy
rbac.create_role("role_viewer", "Viewer", ["perm_read"])
rbac.create_role("role_editor", "Editor", 
                 ["perm_read", "perm_write"], 
                 parent_id="role_viewer")
rbac.create_role("role_admin", "Admin", 
                 ["perm_read", "perm_write", "perm_delete"],
                 parent_id="role_editor")

# Create users
rbac.create_user("user_alice", "alice@example.com", "Alice")
rbac.create_user("user_bob", "bob@example.com", "Bob")

# Assign roles
rbac.assign_role("user_alice", "role_viewer")
rbac.assign_role("user_bob", "role_admin")

# Check permissions
print(f"Alice can read: {rbac.can('user_alice', 'read', 'document')}")
print(f"Alice can write: {rbac.can('user_alice', 'write', 'document')}")
print(f"Bob can delete: {rbac.can('user_bob', 'delete', 'document')}")
```

**Output:**
```
Alice can read: True
Alice can write: False
Bob can delete: True
```

## Advanced: Attribute-Based Access Control (ABAC)

Add conditions to permissions for fine-grained control:

```python
# Only allow reading own documents
perm_read_own = rbac.create_permission(
    permission_id="perm_read_own",
    resource_type="document",
    action="read",
    conditions={
        "resource.owner_id": {"==": "{{user.id}}"}
    }
)

# Only allow editing during business hours
perm_edit_hours = rbac.create_permission(
    permission_id="perm_edit_hours",
    resource_type="document",
    action="write",
    conditions={
        "time.hour": {">": 8, "<": 18},
        "resource.owner_id": {"==": "{{user.id}}"}
    }
)

# Only senior users can delete
perm_delete_senior = rbac.create_permission(
    permission_id="perm_delete_senior",
    resource_type="document",
    action="delete",
    conditions={
        "user.level": {">": 5},
        "resource.status": {"==": "draft"}
    }
)

# Create user with attributes
user = rbac.create_user(
    user_id="user_charlie",
    email="charlie@example.com",
    name="Charlie",
    attributes={"level": 7, "department": "engineering"}
)

# Create resource with attributes
doc = rbac.create_resource(
    resource_id="resource_doc_123",
    resource_type="document",
    attributes={
        "owner_id": "user_charlie",
        "status": "draft",
        "department": "engineering"
    }
)

# Check with resource context
result = rbac.check(
    "user_charlie",
    "delete",
    {"type": "document", "id": "resource_doc_123"}
)

print(f"Can delete: {result['allowed']}")
print(f"Reason: {result['reason']}")
```

## Next Steps

1. **Run Examples:** Check out [examples/](examples/) for complete working examples
2. **Read Protocol Spec:** See [PROTOCOL.md](PROTOCOL.md) for language-agnostic specification
3. **Integration Guide:** See [docs/integration.md](docs/integration.md) for web framework integration
4. **Production Setup:** See [docs/production.md](docs/production.md) for SQL and Redis backends

## Common Use Cases

### Web API Authorization

```python
from flask import Flask, request, jsonify
from rbac import RBAC, PermissionDenied

app = Flask(__name__)
rbac = RBAC(storage='memory')

@app.route('/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    user_id = request.headers.get('X-User-ID')
    
    try:
        rbac.require(user_id, 'read', {'type': 'document', 'id': f'resource_{doc_id}'})
        # Return document
        return jsonify({"document": "content"})
    except PermissionDenied:
        return jsonify({"error": "Access denied"}), 403
```

### Multi-Tenancy

```python
# Create tenant-scoped users and roles
rbac.create_user("user_alice", "alice@acme.com", "Alice", domain="acme")
rbac.create_role("role_admin", "Admin", ["perm_all"], domain="acme")

# Check with domain context
rbac.can("user_alice", "admin", "resource", domain="acme")
```

### Temporary Access

```python
from datetime import datetime, timedelta

# Grant temporary admin access for 1 hour
expires_at = datetime.utcnow() + timedelta(hours=1)
rbac.assign_role(
    "user_alice",
    "role_admin",
    granted_by="user_bob",
    expires_at=expires_at
)
```

## Troubleshooting

**Q: Why does `rbac.can()` always return False?**

A: Check these common issues:
1. User ID must start with `"user_"`
2. Role ID must start with `"role_"`
3. Permission ID must start with `"perm_"`
4. Make sure the role is assigned to the user
5. Verify the permission is added to the role

**Q: How do I debug ABAC conditions?**

A: Use `rbac.check()` instead of `rbac.can()` to get detailed information:

```python
result = rbac.check("user_alice", "write", "document")
print(result['reason'])  # Shows why permission was granted/denied
print(result['matched_permissions'])  # Shows which permissions matched
```

**Q: Can I use this in production?**

A: Yes! But switch from in-memory storage to a persistent backend:

```python
from rbac import RBAC
from rbac.storage import PostgreSQLStorage

storage = PostgreSQLStorage("postgresql://localhost/rbac_db")
rbac = RBAC(storage=storage)
```

## Getting Help

- **Documentation:** [docs/](docs/)
- **Examples:** [examples/](examples/)
- **Issues:** [GitHub Issues](https://github.com/rbac-algorithm/rbac-python/issues)
- **Discussions:** [GitHub Discussions](https://github.com/rbac-algorithm/rbac-python/discussions)
