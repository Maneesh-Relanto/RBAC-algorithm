---
sidebar_position: 1
---

# Introduction

<div style={{textAlign: 'center', margin: '2rem 0'}}>
  <img src="/img/logo.svg" alt="RBAC Algorithm Logo" width="150" style={{marginBottom: '1rem'}} />
</div>

Welcome to **RBAC Algorithm** - a powerful, enterprise-grade Role-Based Access Control library designed for modern applications.

## What is RBAC Algorithm?

RBAC Algorithm provides a comprehensive, language-agnostic solution for implementing fine-grained access control in your applications. Built on industry-standard protocols, it supports:

- 🎯 **Traditional RBAC** - Users, Roles, and Permissions
- 🔐 **ABAC** - Attribute-Based Access Control with dynamic conditions
- 📊 **Role Hierarchies** - Inheritance with automatic permission propagation
- 🏢 **Multi-Tenancy** - Domain isolation for SaaS applications
- 🌐 **Language Agnostic** - Protocol-based with adapters for multiple languages

## Why RBAC Algorithm?

### Simple Yet Powerful

```python
# Check if a user can perform an action
result = rbac.check_permission(
    user_id="user_123",
    action="write",
    resource_id="document_456"
)

if result.allowed:
    # Proceed with operation
    pass
```

### Enterprise-Ready

- **Performance** - Optimized with caching and batch operations
- **Scalable** - From startups to enterprises
- **Auditable** - Complete authorization trails
- **Secure** - Industry best practices baked in

### Developer Experience First

- Clear, intuitive API
- Comprehensive documentation
- Interactive examples
- Multi-language support

## Quick Example

```python
from rbac import RBAC

# Initialize
rbac = RBAC()

# Create permissions
read_perm = rbac.create_permission(
    permission_id="perm_doc_read",
    action="read",
    resource_type="document"
)

# Create role
editor = rbac.create_role(
    role_id="role_editor",
    name="Editor"
)

# Assign permission to role
rbac.assign_permission_to_role("role_editor", "perm_doc_read")

# Assign role to user
rbac.assign_role_to_user("user_123", "role_editor")

# Check permission
result = rbac.check_permission(
    user_id="user_123",
    action="read",
    resource_id="document_456"
)

print(result.allowed)  # True
```

## Next Steps

<div className="button-group">
  <a href="/docs/getting-started/installation" className="button button--primary button--lg">
    Get Started
  </a>
  <a href="/docs/concepts/overview" className="button button--secondary button--lg">
    Learn Concepts
  </a>
  <a href="/playground" className="button button--outline button--lg">
    Try Playground
  </a>
</div>

## Key Features

### Role-Based Access Control

Assign permissions to roles, then assign roles to users. Simple, proven, and effective.

### Attribute-Based Access Control

Go beyond simple role assignments with dynamic conditions:

```python
# Only allow editing own documents during business hours
permission = rbac.create_permission(
    permission_id="perm_edit_own",
    action="edit",
    resource_type="document",
    conditions=[
        {"field": "resource.owner_id", "operator": "==", "value": "{{user.id}}"},
        {"field": "time.hour", "operator": ">", "value": 8},
        {"field": "time.hour", "operator": "<", "value": 18}
    ]
)
```

### Role Hierarchies

Build organizational structures with automatic permission inheritance:

```python
# Admin inherits all Editor permissions
rbac.create_role(
    role_id="role_admin",
    name="Administrator",
    parent_id="role_editor"  # Inherits from Editor
)
```

### Multi-Tenancy

Perfect for SaaS applications with domain isolation:

```python
# Different permissions for different tenants
result = rbac.check_permission(
    user_id="user_123",
    action="read",
    resource_id="document_456",
    domain="tenant_a"
)
```

## Community & Support

- 📖 [Documentation](/docs/getting-started/installation)
- 💬 [GitHub Discussions](https://github.com/your-org/rbac-algorithm/discussions)
- 🐛 [Issue Tracker](https://github.com/your-org/rbac-algorithm/issues)
- 📧 [Email Support](mailto:support@rbac-algorithm.com)
