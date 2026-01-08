---
title: Interactive Playground
---

import RBACPlayground from '@site/src/components/RBACPlayground';

# RBAC Playground

Try RBAC Algorithm right in your browser! Select different scenarios to see how various features work.

<RBACPlayground />

## What Can You Test?

### 1. Basic RBAC
Learn the fundamentals:
- Creating permissions, roles, and users
- Assigning permissions to roles
- Assigning roles to users
- Checking permissions

### 2. Role Hierarchy
Explore inheritance:
- Parent-child role relationships
- Automatic permission propagation
- Multi-level hierarchies

### 3. ABAC (Attribute-Based Access Control)
Test dynamic conditions:
- Resource ownership checks
- User attribute conditions
- Numeric comparisons
- Multiple condition logic

### 4. Multi-Tenancy
See domain isolation:
- Tenant-specific users
- Domain-scoped resources
- Cross-tenant access prevention

## Try It Locally

Want to run these examples on your machine? Install the library:

```bash
pip install rbac-algorithm
```

Then copy any scenario code and run it:

```python
from rbac import RBAC

# Paste playground code here
rbac = RBAC()
# ... rest of code
```

## Need Help?

- 📖 [Documentation](/docs/intro)
- 💬 [GitHub Discussions](https://github.com/your-org/rbac-algorithm/discussions)
- 🐛 [Report Issues](https://github.com/your-org/rbac-algorithm/issues)
