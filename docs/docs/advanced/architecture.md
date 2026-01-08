---
sidebar_position: 1
---

# Architecture

## System Architecture Diagram

![RBAC Architecture](/img/architecture-diagram.svg)

*Complete system architecture showing all layers and components.*

## Overview

RBAC Algorithm uses a layered, protocol-based architecture designed for:

- **Language Agnostic**: Works with any programming language
- **Extensible Storage**: Plug in any backend (SQL, NoSQL, Cloud, Custom)
- **Enterprise Grade**: Multi-tenancy, role hierarchies, ABAC support
- **Clean Architecture**: Clear separation of concerns

## Architecture Layers

### 1. Application Layer
Your application interacts with the RBAC system through the main API:
- `RBAC` class - Primary entry point
- Batch operations for bulk processing
- Multi-tenant domain isolation

### 2. Protocol Layer
Language-agnostic interfaces that define contracts:
- `IStorageProvider` - CRUD + indexes + batch operations
- `IAuthorizationEngine` - Permission checks and context evaluation
- `IRoleHierarchyResolver` - Role inheritance and DAG validation
- `IPolicyEvaluator` - ABAC rules with 12 operators

### 3. Implementation Layer
Concrete implementations of protocol interfaces:
- `MemoryStorage` - In-memory storage (750+ lines)
- `AuthEngine` - Authorization engine (540+ lines)
- `HierarchyResolver` - Role hierarchy (390+ lines)
- `PolicyEvaluator` - ABAC engine (380+ lines)

### 4. Data Models
Core entities with domain isolation:
- `User` - User entity
- `Role` - Role with permissions
- `Permission` - Action + resource pattern
- `Resource` - Protected resource
- `RoleAssignment` - User-role mapping
- `RoleInheritance` - Role hierarchy

### 5. Storage Backends
Extensible storage layer:
- SQL databases (PostgreSQL, MySQL)
- NoSQL databases (MongoDB, DynamoDB)
- Cloud storage (S3, Azure Blob)
- Custom backends (implement `IStorageProvider`)

## Key Design Principles

### Protocol-Based Design
All core functionality is defined as protocols (interfaces), allowing:
- Easy testing with mocks
- Multiple implementations
- Language portability

### Multi-Tenancy First
Every entity includes a `domain` field for organization isolation:
```python
user = User(id="user1", domain="acme-corp")
role = Role(id="admin", domain="acme-corp")
```

### Performance Optimized
- Indexed lookups for fast queries
- Batch operations to reduce round trips
- Caching support in storage layer

### Security by Default
- Domain isolation prevents cross-tenant access
- Explicit permission checks (deny by default)
- Audit trail support

## Extension Points

### Custom Storage Backend
Implement `IStorageProvider` to use your preferred database:
```python
class PostgresStorage(IStorageProvider):
    def create_user(self, user: User) -> User:
        # Your implementation
```

### Custom Policy Evaluator
Extend `IPolicyEvaluator` for custom business rules:
```python
class CustomEvaluator(IPolicyEvaluator):
    def evaluate(self, condition: Dict, context: Dict) -> bool:
        # Your custom logic
```

### Custom Authorization Engine
Replace the entire authorization logic if needed:
```python
class CustomEngine(IAuthorizationEngine):
    def check_permission(self, user_id: str, action: str, resource_id: str, domain: str) -> bool:
        # Your implementation
```

## Learn More

- [Protocol Specification](https://github.com/yourusername/rbac-algorithm/blob/main/documentation/architecture/PROTOCOL.md)
- [Adapter Guidelines](https://github.com/yourusername/rbac-algorithm/blob/main/documentation/architecture/ADAPTERS.md)
- [API Reference](/docs/api/overview)
