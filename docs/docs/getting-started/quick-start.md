---
sidebar_position: 2
---

# Quick Start

Learn RBAC Algorithm basics in 5 minutes.

## Basic Setup

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="python" label="Python" default>

```python
from rbac import RBAC

# Initialize with in-memory storage
rbac = RBAC()
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
const { RBAC } = require('rbac-algorithm');

// Initialize with in-memory storage
const rbac = new RBAC();
```

</TabItem>
</Tabs>

## Core Workflow

### 1. Create Permissions

Permissions define **what actions** can be performed on **what resources**.

<Tabs>
<TabItem value="python" label="Python" default>

```python
# Create a permission to read documents
read_docs = rbac.create_permission(
    permission_id="perm_doc_read",
    action="read",
    resource_type="document",
    description="Allows reading documents"
)

# Create more permissions
write_docs = rbac.create_permission(
    permission_id="perm_doc_write",
    action="write",
    resource_type="document"
)

delete_docs = rbac.create_permission(
    permission_id="perm_doc_delete",
    action="delete",
    resource_type="document"
)
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
// Create a permission to read documents
const readDocs = rbac.createPermission({
    permissionId: "perm_doc_read",
    action: "read",
    resourceType: "document",
    description: "Allows reading documents"
});

// Create more permissions
const writeDocs = rbac.createPermission({
    permissionId: "perm_doc_write",
    action: "write",
    resourceType: "document"
});

const deleteDocs = rbac.createPermission({
    permissionId: "perm_doc_delete",
    action: "delete",
    resourceType: "document"
});
```

</TabItem>
</Tabs>

### 2. Create Roles

Roles are collections of permissions.

<Tabs>
<TabItem value="python" label="Python" default>

```python
# Create Viewer role
viewer = rbac.create_role(
    role_id="role_viewer",
    name="Viewer",
    description="Can only read documents"
)

# Create Editor role
editor = rbac.create_role(
    role_id="role_editor",
    name="Editor",
    description="Can read and write documents"
)

# Create Admin role
admin = rbac.create_role(
    role_id="role_admin",
    name="Administrator",
    description="Full access to documents"
)
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
// Create Viewer role
const viewer = rbac.createRole({
    roleId: "role_viewer",
    name: "Viewer",
    description: "Can only read documents"
});

// Create Editor role
const editor = rbac.createRole({
    roleId: "role_editor",
    name: "Editor",
    description: "Can read and write documents"
});

// Create Admin role
const admin = rbac.createRole({
    roleId: "role_admin",
    name: "Administrator",
    description: "Full access to documents"
});
```

</TabItem>
</Tabs>

### 3. Assign Permissions to Roles

<Tabs>
<TabItem value="python" label="Python" default>

```python
# Viewer can only read
rbac.assign_permission_to_role("role_viewer", "perm_doc_read")

# Editor can read and write
rbac.assign_permission_to_role("role_editor", "perm_doc_read")
rbac.assign_permission_to_role("role_editor", "perm_doc_write")

# Admin has all permissions
rbac.assign_permission_to_role("role_admin", "perm_doc_read")
rbac.assign_permission_to_role("role_admin", "perm_doc_write")
rbac.assign_permission_to_role("role_admin", "perm_doc_delete")
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
// Viewer can only read
rbac.assignPermissionToRole("role_viewer", "perm_doc_read");

// Editor can read and write
rbac.assignPermissionToRole("role_editor", "perm_doc_read");
rbac.assignPermissionToRole("role_editor", "perm_doc_write");

// Admin has all permissions
rbac.assignPermissionToRole("role_admin", "perm_doc_read");
rbac.assignPermissionToRole("role_admin", "perm_doc_write");
rbac.assignPermissionToRole("role_admin", "perm_doc_delete");
```

</TabItem>
</Tabs>

### 4. Create Users

<Tabs>
<TabItem value="python" label="Python" default>

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

carol = rbac.create_user(
    user_id="user_carol",
    email="carol@example.com",
    name="Carol Williams"
)
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
// Create users
const alice = rbac.createUser({
    userId: "user_alice",
    email: "alice@example.com",
    name: "Alice Johnson"
});

const bob = rbac.createUser({
    userId: "user_bob",
    email: "bob@example.com",
    name: "Bob Smith"
});

const carol = rbac.createUser({
    userId: "user_carol",
    email: "carol@example.com",
    name: "Carol Williams"
});
```

</TabItem>
</Tabs>

### 5. Assign Roles to Users

<Tabs>
<TabItem value="python" label="Python" default>

```python
# Alice is a Viewer
rbac.assign_role_to_user("user_alice", "role_viewer")

# Bob is an Editor
rbac.assign_role_to_user("user_bob", "role_editor")

# Carol is an Admin
rbac.assign_role_to_user("user_carol", "role_admin")
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
// Alice is a Viewer
rbac.assignRoleToUser("user_alice", "role_viewer");

// Bob is an Editor
rbac.assignRoleToUser("user_bob", "role_editor");

// Carol is an Admin
rbac.assignRoleToUser("user_carol", "role_admin");
```

</TabItem>
</Tabs>

### 6. Check Permissions

<Tabs>
<TabItem value="python" label="Python" default>

```python
# Can Alice read a document?
result = rbac.check_permission(
    user_id="user_alice",
    action="read",
    resource_id="document_123"
)
print(result.allowed)  # True

# Can Alice write a document?
result = rbac.check_permission(
    user_id="user_alice",
    action="write",
    resource_id="document_123"
)
print(result.allowed)  # False

# Can Bob write a document?
result = rbac.check_permission(
    user_id="user_bob",
    action="write",
    resource_id="document_123"
)
print(result.allowed)  # True

# Get detailed information
result = rbac.check_permission_detailed(
    user_id="user_bob",
    action="write",
    resource_id="document_123"
)
print(result.reason)  # "Allowed by permission(s): perm_doc_write"
print(result.matched_permissions)  # ["perm_doc_write"]
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
// Can Alice read a document?
let result = rbac.checkPermission({
    userId: "user_alice",
    action: "read",
    resourceId: "document_123"
});
console.log(result.allowed);  // true

// Can Alice write a document?
result = rbac.checkPermission({
    userId: "user_alice",
    action: "write",
    resourceId: "document_123"
});
console.log(result.allowed);  // false

// Can Bob write a document?
result = rbac.checkPermission({
    userId: "user_bob",
    action: "write",
    resourceId: "document_123"
});
console.log(result.allowed);  // true

// Get detailed information
result = rbac.checkPermissionDetailed({
    userId: "user_bob",
    action: "write",
    resourceId: "document_123"
});
console.log(result.reason);  // "Allowed by permission(s): perm_doc_write"
console.log(result.matchedPermissions);  // ["perm_doc_write"]
```

</TabItem>
</Tabs>

## Complete Example

<Tabs>
<TabItem value="python" label="Python" default>

```python
from rbac import RBAC

# Initialize
rbac = RBAC()

# Setup permissions
rbac.create_permission("perm_read", "read", "document")
rbac.create_permission("perm_write", "write", "document")

# Setup role
rbac.create_role("role_editor", "Editor")
rbac.assign_permission_to_role("role_editor", "perm_read")
rbac.assign_permission_to_role("role_editor", "perm_write")

# Setup user
rbac.create_user("user_123", "user@example.com", "John Doe")
rbac.assign_role_to_user("user_123", "role_editor")

# Check permission
result = rbac.check_permission(
    user_id="user_123",
    action="write",
    resource_id="document_456"
)

if result.allowed:
    print("✓ Access granted!")
else:
    print("✗ Access denied!")
```

</TabItem>
<TabItem value="javascript" label="JavaScript">

```javascript
const { RBAC } = require('rbac-algorithm');

// Initialize
const rbac = new RBAC();

// Setup permissions
rbac.createPermission({permissionId: "perm_read", action: "read", resourceType: "document"});
rbac.createPermission({permissionId: "perm_write", action: "write", resourceType: "document"});

// Setup role
rbac.createRole({roleId: "role_editor", name: "Editor"});
rbac.assignPermissionToRole("role_editor", "perm_read");
rbac.assignPermissionToRole("role_editor", "perm_write");

// Setup user
rbac.createUser({userId: "user_123", email: "user@example.com", name: "John Doe"});
rbac.assignRoleToUser("user_123", "role_editor");

// Check permission
const result = rbac.checkPermission({
    userId: "user_123",
    action: "write",
    resourceId: "document_456"
});

if (result.allowed) {
    console.log("✓ Access granted!");
} else {
    console.log("✗ Access denied!");
}
```

</TabItem>
</Tabs>

## What's Next?

- 🏗️ [Build Your First App](/docs/getting-started/first-app) - Complete tutorial
- 📚 [Core Concepts](/docs/concepts/overview) - Deep dive into RBAC
- 🔐 [ABAC Guide](/docs/guides/attribute-based) - Dynamic conditions
- 📊 [Role Hierarchies](/docs/guides/hierarchical-roles) - Inheritance patterns
