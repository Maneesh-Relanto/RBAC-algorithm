---
sidebar_position: 1
---

# FAQ - Frequently Asked Questions

Get quick answers to common questions about RBAC Algorithm.

## General Questions

### What is RBAC Algorithm?

RBAC Algorithm is an enterprise-grade, language-agnostic access control library that combines traditional Role-Based Access Control (RBAC) with Attribute-Based Access Control (ABAC). It provides a clean API, excellent developer experience, and scales from startups to enterprises.

### Why choose RBAC Algorithm over other solutions?

- ✅ **Simple yet powerful** - Easy to get started, scales to complex use cases
- ✅ **Language agnostic** - Protocol-based design with adapters for multiple languages
- ✅ **Enterprise-ready** - Multi-tenancy, audit logs, performance optimizations
- ✅ **Well documented** - Comprehensive guides, examples, and API reference
- ✅ **Active development** - Regular updates and community support

### Is it production-ready?

Yes! RBAC Algorithm is designed for production use with:
- Comprehensive test coverage
- Performance optimizations (caching, batch operations)
- Multiple storage backend support
- Security best practices baked in
- Regular security updates

### What's the license?

[Check your repository for the specific license - typically MIT or Apache 2.0]

## Technical Questions

### Which programming languages are supported?

**Currently Available:**
- Python 3.8+
- JavaScript/Node.js 16+

**Coming Soon:**
- Go
- Java
- C#/.NET
- Ruby

See [Language Adapters](/docs/adapters/overview) for details.

### Can I use my own database?

Yes! RBAC Algorithm uses a protocol-based storage architecture. We provide:

**Built-in:**
- In-memory (development/testing)
- PostgreSQL
- MongoDB
- Redis

**Custom:**
Implement the `IStorageProvider` protocol to use any database. See [Custom Storage Guide](/docs/guides/custom-storage).

### How does performance compare to other RBAC libraries?

RBAC Algorithm is optimized for production workloads:

- **Caching** - Frequently accessed data cached automatically
- **Batch Operations** - Check multiple permissions in one call
- **Lazy Loading** - Load data only when needed
- **Indexing** - Storage backends use appropriate indexes

Benchmarks show comparable or better performance than popular alternatives.

### Is it thread-safe?

Yes, with caveats:

- **In-memory storage** - Thread-safe for read operations, requires locks for writes
- **Database backends** - Thread-safe via database transactions
- **Immutable models** - Core data structures are immutable (frozen dataclasses)

For high-concurrency scenarios, use a database backend with proper connection pooling.

## Feature Questions

### What's the difference between RBAC and ABAC?

**RBAC (Role-Based Access Control):**
- Permissions assigned to roles
- Users assigned to roles
- Static, role-based decisions
- Simple and fast

**ABAC (Attribute-Based Access Control):**
- Dynamic conditions on permissions
- Based on user, resource, and context attributes
- Flexible and fine-grained
- More complex

**RBAC Algorithm supports both!** Use RBAC for simplicity, add ABAC when you need fine-grained control.

```python
# RBAC: Simple role check
rbac.assign_role_to_user("user_123", "role_editor")

# ABAC: Dynamic conditions
permission = rbac.create_permission(
    permission_id="perm_edit_own",
    action="edit",
    resource_type="document",
    conditions=[
        {"field": "resource.owner_id", "operator": "==", "value": "{{user.id}}"}
    ]
)
```

### Do I need to choose between RBAC and ABAC?

No! You can use both together. Common pattern:

1. Use **RBAC** for broad permissions (role-based)
2. Add **ABAC** for fine-grained rules (attribute-based)

Example:
```python
# Role grants base permission
rbac.assign_role_to_user("user_123", "role_author")

# Permission has ABAC condition
# Author role includes "edit own documents" permission with condition
```

### Can roles inherit from multiple parents?

Currently, each role can have **one parent** (single inheritance). This keeps the hierarchy simple and prevents diamond problem complexity.

For multiple capabilities, assign multiple roles to a user:
```python
rbac.assign_role_to_user("user_123", "role_developer")
rbac.assign_role_to_user("user_123", "role_reviewer")
```

### How do I implement "deny" rules?

RBAC Algorithm follows **"deny by default"** principle:
- No permission = Access denied
- Explicit permission required for access

For explicit deny rules, use ABAC conditions:
```python
# Only allow if NOT in blocked list
conditions=[
    {"field": "user.id", "operator": "not_in", "value": blocked_users}
]
```

### Can I expire roles or permissions?

Yes! Use temporary role assignments:

```python
from datetime import datetime, timedelta

# Grant temporary admin access
expires_at = datetime.utcnow() + timedelta(hours=2)

rbac.assign_role_to_user(
    user_id="user_123",
    role_id="role_admin",
    expires_at=expires_at
)

# Automatically expires after 2 hours
```

### How do I audit access decisions?

Enable audit logging in your storage backend:

```python
rbac = RBAC(storage=storage, enable_audit=True)

# All check_permission calls are logged
result = rbac.check_permission(...)

# Query audit logs
logs = rbac.get_audit_logs(
    user_id="user_123",
    start_date=yesterday,
    end_date=today
)
```

## Multi-Tenancy Questions

### How does multi-tenancy work?

Each entity (user, role, resource) can have an optional `domain` field:

```python
# Create user in tenant A
rbac.create_user("user_a", "a@example.com", domain="tenant_a")

# Create resource in tenant A
rbac.create_resource("doc_1", "document", domain="tenant_a")

# Check permission with domain isolation
rbac.check_permission(
    user_id="user_a",
    action="read",
    resource_id="doc_1",
    domain="tenant_a"  # Must match
)
```

### Can users belong to multiple tenants?

Create separate user records per tenant:

```python
# User in tenant A
rbac.create_user("user_123_tenant_a", "user@example.com", domain="tenant_a")

# Same user in tenant B
rbac.create_user("user_123_tenant_b", "user@example.com", domain="tenant_b")
```

### How do I share resources across tenants?

Omit the `domain` field to create global resources:

```python
# Global resource accessible by all tenants
rbac.create_resource("public_doc", "document", domain=None)
```

## Migration & Integration

### Can I migrate from another RBAC library?

Yes! Common migration path:

1. **Export data** from old system
2. **Map to RBAC Algorithm models** (User, Role, Permission)
3. **Import using bulk operations**
4. **Test thoroughly** before switching
5. **Run both systems** temporarily during transition

See [Migration Guide](/docs/advanced/migration) for specific library migrations.

### How do I integrate with my authentication system?

RBAC Algorithm handles **authorization** (what you can do), not **authentication** (who you are).

Integration pattern:
```python
# 1. User authenticates (your auth system)
user_id = your_auth_system.authenticate(credentials)

# 2. Check authorization (RBAC Algorithm)
can_access = rbac.check_permission(
    user_id=user_id,
    action="write",
    resource_id="document_123"
)
```

Works with any auth system: OAuth, JWT, SAML, etc.

### Can I use it with GraphQL/REST/gRPC?

Yes! RBAC Algorithm is transport-agnostic. Common patterns:

**REST Middleware:**
```python
@app.before_request
def check_permissions():
    user_id = get_current_user()
    resource_id = extract_resource_from_path()
    action = request.method.lower()
    
    if not rbac.check_permission(user_id, action, resource_id).allowed:
        abort(403)
```

**GraphQL:**
```python
@requires_permission(action="read", resource_type="user")
def resolve_user(parent, info, user_id):
    return User.get(user_id)
```

## Troubleshooting

### Permission check returns False unexpectedly

**Checklist:**
1. ✅ User has role assigned?
2. ✅ Role has permission assigned?
3. ✅ Permission action/resource_type matches?
4. ✅ ABAC conditions satisfied?
5. ✅ Domain matches (if multi-tenant)?

**Debug:**
```python
# Get detailed info
result = rbac.check_permission_detailed(user_id, action, resource_id)
print(result.reason)  # Why allowed/denied
print(result.matched_permissions)  # Which permissions matched
```

### Role hierarchy not working

**Common issues:**
1. Circular dependency (role inherits from itself)
2. Parent role doesn't exist
3. Permissions not assigned to parent role

**Fix:**
```python
# Validate hierarchy
try:
    rbac.validate_role_hierarchy("role_id")
except CircularDependencyError:
    print("Circular dependency detected!")
```

### Performance is slow

**Optimization checklist:**
1. ✅ Use database backend (not in-memory) for production
2. ✅ Enable caching
3. ✅ Use batch operations for multiple checks
4. ✅ Add database indexes
5. ✅ Profile and optimize queries

```python
# Use batch checks
results = rbac.batch_check([
    {"user_id": "user_1", "action": "read", "resource_id": "doc_1"},
    {"user_id": "user_1", "action": "write", "resource_id": "doc_1"}
])
```

## Contributing

### How can I contribute?

We welcome contributions!

- 🐛 **Bug Reports** - [GitHub Issues](https://github.com/your-org/rbac-algorithm/issues)
- 💡 **Feature Requests** - [Discussions](https://github.com/your-org/rbac-algorithm/discussions)
- 📝 **Documentation** - Submit PRs for doc improvements
- 💻 **Code** - See [Contributing Guide](/docs/contributing)

### I found a security issue

**DO NOT** open a public issue. Email: security@rbac-algorithm.com

See [Security Policy](/docs/advanced/security) for details.

## Still Have Questions?

- 💬 [GitHub Discussions](https://github.com/your-org/rbac-algorithm/discussions)
- 📧 [Email Support](mailto:support@rbac-algorithm.com)
- 📖 [Full Documentation](/docs/intro)
- 🚀 [Interactive Playground](/playground)
