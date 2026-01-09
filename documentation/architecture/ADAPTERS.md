# Language Adapters Guide

## System Architecture

![RBAC Architecture](../../docs/static/img/architecture-diagram.svg)

*🎨 Enhanced protocol-based architecture - Verified against codebase (96% accuracy), showing clear separation between protocols and implementations for multi-language adapter support. [Edit diagram](../../docs/static/img/architecture-diagram.drawio) in [diagrams.net](https://app.diagrams.net/)*

## Overview

This document describes how to implement RBAC Algorithm adapters for different programming languages. Each adapter provides an idiomatic interface while adhering to the core protocol specification.

## Adapter Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Language-Agnostic Core                  │
│                   (PROTOCOL.md Spec)                     │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
┌───────────▼──────────┐ ┌──▼───────────┐ ┌▼──────────────┐
│   Python Adapter     │ │ Node.js      │ │ Go Adapter    │
│   (Reference Impl)   │ │ Adapter      │ │               │
└──────────────────────┘ └──────────────┘ └───────────────┘
            │               │               │
┌───────────▼──────────┐ ┌──▼───────────┐ ┌▼──────────────┐
│  Python Apps/        │ │ Express/     │ │ Go Web Apps   │
│  Django/Flask        │ │ Nest.js      │ │               │
└──────────────────────┘ └──────────────┘ └───────────────┘
```

## Adapter Structure

Each language adapter MUST provide:

### 1. Core Components

```
language-adapter/
├── README.md                 # Getting started
├── LICENSE                   # MIT License
├── CHANGELOG.md             # Version history
├── package.[json|yaml]      # Dependencies
│
├── src/
│   ├── models/              # Data models
│   │   ├── user
│   │   ├── role
│   │   ├── permission
│   │   └── resource
│   │
│   ├── storage/             # Storage providers
│   │   ├── interface
│   │   ├── memory
│   │   ├── sql
│   │   └── redis
│   │
│   ├── engine/              # Authorization engine
│   │   ├── authorizer
│   │   ├── hierarchy
│   │   └── evaluator
│   │
│   ├── cache/               # Caching layer
│   ├── audit/               # Audit logging
│   ├── exceptions/          # Error types
│   └── index               # Main export
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── performance/
│
├── examples/
│   ├── basic/
│   ├── advanced/
│   └── frameworks/
│
└── docs/
    ├── api/
    └── guides/
```

### 2. Public API

Every adapter MUST expose:

```
// JavaScript/TypeScript Example
import { RBAC, User, Role, Permission } from 'rbac-algorithm';

const rbac = new RBAC({
  storage: 'memory', // or sql, redis, etc.
  cache: { enabled: true, ttl: 300 },
  audit: { enabled: true }
});

// Core operations
await rbac.can(userId, action, resource);
await rbac.assignRole(userId, roleId);
await rbac.createRole(role);
await rbac.getUserPermissions(userId);
```

### 3. JSON Schema Validation

All adapters MUST validate input against JSON schemas:

```javascript
// Validate user creation
const userSchema = require('./schemas/user.schema.json');
validate(userData, userSchema);
```

## Language-Specific Guidelines

### Python Adapter (Reference Implementation)

**Package Structure**:
```python
# Installation
pip install rbac-algorithm

# Usage
from rbac import RBAC, User, Role, Permission

rbac = RBAC(storage='memory')
allowed = rbac.can(user_id, action, resource)
```

**Key Conventions**:
- Use `snake_case` for functions/variables
- Type hints for all public APIs
- Dataclasses for models
- Context managers for resources
- Async support via `asyncio`

**Example**:
```python
from rbac import RBAC
from rbac.storage import PostgreSQLStorage

# Initialize
storage = PostgreSQLStorage(connection_string="postgresql://...")
rbac = RBAC(storage=storage)

# Check permission
result = rbac.check_permission(
    user_id="user_123",
    action="read",
    resource={"type": "document", "id": "doc_456"}
)

# Async version
async with RBAC(storage="postgresql://...") as rbac:
    result = await rbac.check_permission_async(...)
```

### Node.js/TypeScript Adapter

**Package Structure**:
```typescript
// Installation
npm install rbac-algorithm

// TypeScript usage
import { RBAC, User, Role, Permission } from 'rbac-algorithm';

const rbac = new RBAC({ storage: 'memory' });
const allowed = await rbac.can(userId, action, resource);
```

**Key Conventions**:
- Use `camelCase` for functions/variables
- Full TypeScript definitions
- Promise-based async APIs
- Event emitters for audit logs
- Express/NestJS middleware

**Example**:
```typescript
import { RBAC, MemoryStorage } from 'rbac-algorithm';

// Initialize
const rbac = new RBAC({
  storage: new MemoryStorage(),
  cache: { 
    enabled: true, 
    provider: 'redis',
    url: 'redis://localhost:6379'
  }
});

// Check permission
const result = await rbac.checkPermission({
  userId: 'user_123',
  action: 'read',
  resource: {
    type: 'document',
    id: 'doc_456'
  }
});

// Express middleware
import { requirePermission } from 'rbac-algorithm/express';

app.get('/documents/:id', 
  requirePermission('document', 'read'),
  (req, res) => { /* handler */ }
);
```

### Go Adapter

**Package Structure**:
```go
// Installation
go get github.com/rbac-algorithm/rbac-go

// Usage
import "github.com/rbac-algorithm/rbac-go"

rbac := rbac.New(rbac.Config{Storage: "memory"})
allowed, err := rbac.Can(userID, action, resource)
```

**Key Conventions**:
- Use `PascalCase` for exports
- Error returns (no exceptions)
- Interfaces for extensibility
- Context for cancellation
- goroutine-safe operations

**Example**:
```go
package main

import (
    "context"
    rbac "github.com/rbac-algorithm/rbac-go"
    "github.com/rbac-algorithm/rbac-go/storage/postgres"
)

func main() {
    // Initialize
    storage := postgres.New("postgresql://...")
    engine := rbac.New(rbac.Config{
        Storage: storage,
        Cache: rbac.CacheConfig{
            Enabled: true,
            TTL: 300,
        },
    })
    defer engine.Close()
    
    // Check permission
    ctx := context.Background()
    result, err := engine.CheckPermission(ctx, rbac.CheckRequest{
        UserID: "user_123",
        Action: "read",
        Resource: rbac.Resource{
            Type: "document",
            ID: "doc_456",
        },
    })
    
    if err != nil {
        log.Fatal(err)
    }
    
    if result.Allowed {
        // Grant access
    }
}
```

### Java Adapter

**Package Structure**:
```java
// Maven
<dependency>
    <groupId>com.rbac-algorithm</groupId>
    <artifactId>rbac-java</artifactId>
    <version>1.0.0</version>
</dependency>

// Usage
import com.rbac.RBAC;

RBAC rbac = new RBAC.Builder()
    .storage("memory")
    .build();
    
boolean allowed = rbac.can(userId, action, resource);
```

**Key Conventions**:
- Use `camelCase` for methods
- Builder pattern for configuration
- CompletableFuture for async
- Streaming API for batch operations
- Annotation-based (Spring)

**Example**:
```java
import com.rbac.RBAC;
import com.rbac.storage.PostgreSQLStorage;
import com.rbac.models.*;

// Initialize
Storage storage = new PostgreSQLStorage("jdbc:postgresql://...");
RBAC rbac = new RBAC.Builder()
    .storage(storage)
    .cache(CacheConfig.builder()
        .enabled(true)
        .ttl(300)
        .build())
    .build();

// Check permission
CheckRequest request = CheckRequest.builder()
    .userId("user_123")
    .action("read")
    .resource(Resource.builder()
        .type("document")
        .id("doc_456")
        .build())
    .build();

AuthorizationResult result = rbac.checkPermission(request);

if (result.isAllowed()) {
    // Grant access
}

// Spring annotation
@PreAuthorize("@rbac.can(#userId, 'read', #documentId)")
public Document getDocument(String userId, String documentId) {
    // ...
}
```

## Implementation Checklist

### Phase 1: Core Models ✓
- [ ] User/Subject model
- [ ] Role model with hierarchy
- [ ] Permission model
- [ ] Resource model
- [ ] Serialization (JSON)
- [ ] Validation against schemas

### Phase 2: Storage Layer
- [ ] Storage interface
- [ ] In-memory implementation
- [ ] SQL adapter (PostgreSQL/MySQL)
- [ ] Redis adapter
- [ ] Connection pooling
- [ ] Transaction support

### Phase 3: Authorization Engine
- [ ] Permission checker
- [ ] Role hierarchy resolver
- [ ] ABAC policy evaluator
- [ ] Batch operations
- [ ] Performance optimization

### Phase 4: Caching
- [ ] Cache interface
- [ ] Memory cache
- [ ] Redis cache
- [ ] Cache invalidation
- [ ] TTL support

### Phase 5: Additional Features
- [ ] Audit logging
- [ ] Metrics/monitoring
- [ ] Configuration management
- [ ] Error handling
- [ ] CLI tools

### Phase 6: Testing
- [ ] Unit tests (>90% coverage)
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Compatibility tests
- [ ] Security audits

### Phase 7: Documentation
- [ ] API reference
- [ ] Getting started guide
- [ ] Migration guide
- [ ] Best practices
- [ ] Code examples

### Phase 8: CI/CD
- [ ] Automated testing
- [ ] Code quality checks
- [ ] Security scanning
- [ ] Package publishing
- [ ] Version management

## Testing Requirements

### Unit Tests

```python
# Python example
def test_check_permission_allowed():
    rbac = RBAC(storage='memory')
    user = create_test_user()
    role = create_test_role_with_permissions()
    rbac.assign_role(user.id, role.id)
    
    result = rbac.check_permission(
        user.id, 'read', 
        Resource(type='document', id='doc_1')
    )
    
    assert result['allowed'] == True
    assert 'perm_doc_read' in result['matched_permissions']
```

### Integration Tests

```javascript
// Node.js example
describe('RBAC Integration', () => {
  let rbac;
  
  beforeEach(async () => {
    rbac = new RBAC({ storage: 'postgresql://test_db' });
    await rbac.initialize();
  });
  
  it('should enforce role hierarchy', async () => {
    const admin = await rbac.createRole({
      id: 'admin',
      permissions: ['all']
    });
    
    const editor = await rbac.createRole({
      id: 'editor',
      permissions: ['write'],
      parentId: 'admin'
    });
    
    await rbac.assignRole('user_1', 'editor');
    
    const result = await rbac.can('user_1', 'all', resource);
    expect(result).toBe(true); // Inherited from admin
  });
});
```

### Performance Benchmarks

All adapters MUST meet these benchmarks:

| Operation | Target | Maximum |
|-----------|--------|---------|
| Simple check (memory) | < 0.5ms | 1ms |
| With hierarchy (depth 3) | < 2ms | 5ms |
| With ABAC | < 5ms | 10ms |
| Batch check (100 items) | < 50ms | 100ms |
| Role assignment | < 10ms | 50ms |

## Release Process

1. **Version Bump**: Follow semantic versioning
2. **Changelog**: Update CHANGELOG.md
3. **Tests**: All tests must pass
4. **Documentation**: Update if APIs changed
5. **Build**: Create distribution packages
6. **Publish**: To package registry
7. **Tag**: Create git tag
8. **Announce**: Release notes

## Support Matrix

| Language | Version | Status | Maintainer |
|----------|---------|--------|------------|
| Python | 3.8+ | ✅ Stable | Core team |
| Node.js | 16+ | ✅ Stable | Core team |
| TypeScript | 4.5+ | ✅ Stable | Core team |
| Go | 1.18+ | 🚧 Beta | Community |
| Java | 11+ | 🚧 Beta | Community |
| .NET/C# | 6.0+ | 📝 Planned | Community |
| Rust | 1.60+ | 📝 Planned | Community |
| PHP | 8.0+ | 📝 Planned | Community |

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Code style
- Testing requirements
- Documentation standards
- Pull request process

## Resources

- Protocol Specification: [PROTOCOL.md](../PROTOCOL.md)
- JSON Schemas: [/schemas](../schemas/)
- Examples: [/examples](../examples/)
- API Reference: [/docs/api](../docs/api/)
