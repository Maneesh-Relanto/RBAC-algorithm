# RBAC Protocol Specification v1.0

**Status**: Draft  
**Date**: January 8, 2026  
**Authors**: RBAC Algorithm Contributors  

## Architecture Overview

![RBAC Architecture](../../docs/static/img/architecture-diagram.svg)

*✨ Protocol-based architecture diagram - Enhanced with colorful icons showing IStorageProvider, IAuthorizationEngine, IRoleHierarchyResolver, and IPolicyEvaluator interfaces. [Edit diagram](../../docs/static/img/architecture-diagram.drawio) in [diagrams.net](https://app.diagrams.net/)*

## Abstract

This document defines a language-agnostic protocol for Role-Based Access Control (RBAC) that can be implemented in any programming language. The protocol ensures interoperability, consistency, and portability across different technology stacks.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Data Models](#data-models)
4. [Protocol Operations](#protocol-operations)
5. [Storage Interface](#storage-interface)
6. [Wire Format](#wire-format)
7. [Error Codes](#error-codes)
8. [Implementation Guidelines](#implementation-guidelines)

---

## 1. Overview

### 1.1 Goals

- **Language Agnostic**: Any language can implement this protocol
- **Interoperable**: Different implementations can communicate
- **Extensible**: Easy to add new features without breaking compatibility
- **Performance**: Optimized for high-throughput authorization checks
- **Simple**: Easy to understand and implement

### 1.2 Design Principles

1. **JSON as Exchange Format**: Human-readable, universally supported
2. **REST-first**: HTTP/REST for network operations
3. **Versioned APIs**: Explicit versioning for backward compatibility
4. **Clear Contracts**: Well-defined interfaces and behaviors
5. **Fail-safe Defaults**: Deny by default, explicit grants

---

## 2. Core Concepts

### 2.1 Entities

```
Subject (User)
    ↓ assigned to
  Role
    ↓ grants
Permission
    ↓ on
Resource
```

### 2.2 Authorization Model

The system follows the **NIST RBAC Reference Model**:

- **Core RBAC**: Users, Roles, Permissions, Sessions
- **Hierarchical RBAC**: Role inheritance
- **Constrained RBAC**: Separation of duties (future)
- **Symmetric RBAC**: Permission-role review (future)

---

## 3. Data Models

All models are defined using JSON Schema for language independence.

### 3.1 User (Subject)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "User",
  "required": ["id", "email"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier",
      "pattern": "^[a-zA-Z0-9_-]+$"
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "User email address"
    },
    "name": {
      "type": "string",
      "description": "Display name"
    },
    "attributes": {
      "type": "object",
      "description": "Additional attributes for ABAC",
      "additionalProperties": true
    },
    "status": {
      "type": "string",
      "enum": ["active", "inactive", "suspended", "deleted"],
      "default": "active"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### 3.2 Role

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Role",
  "required": ["id", "name"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier"
    },
    "name": {
      "type": "string",
      "description": "Human-readable name"
    },
    "description": {
      "type": "string",
      "description": "Role description"
    },
    "permissions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of permission IDs"
    },
    "parent_id": {
      "type": ["string", "null"],
      "description": "Parent role for inheritance"
    },
    "domain": {
      "type": ["string", "null"],
      "description": "Domain/tenant isolation"
    },
    "status": {
      "type": "string",
      "enum": ["active", "inactive", "suspended", "deleted"],
      "default": "active"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": true
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### 3.3 Permission

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Permission",
  "required": ["id", "resource_type", "action"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier"
    },
    "resource_type": {
      "type": "string",
      "description": "Type of resource (e.g., 'document', 'api')"
    },
    "action": {
      "type": "string",
      "description": "Action (e.g., 'read', 'write', 'delete', '*')"
    },
    "description": {
      "type": "string",
      "description": "Human-readable description"
    },
    "conditions": {
      "type": "object",
      "description": "ABAC conditions",
      "additionalProperties": true
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### 3.4 Resource

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Resource",
  "required": ["id", "type"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier"
    },
    "type": {
      "type": "string",
      "description": "Resource type matching permission.resource_type"
    },
    "attributes": {
      "type": "object",
      "description": "Resource attributes for ABAC",
      "additionalProperties": true
    },
    "parent_id": {
      "type": ["string", "null"],
      "description": "Parent resource for hierarchies"
    },
    "domain": {
      "type": ["string", "null"],
      "description": "Domain/tenant"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

---

## 4. Protocol Operations

### 4.1 Authorization Check

**Operation**: `check_permission`

**Input**:
```json
{
  "user_id": "string",
  "action": "string",
  "resource": {
    "type": "string",
    "id": "string",
    "attributes": {}
  },
  "context": {
    "domain": "string",
    "timestamp": "ISO8601",
    "ip_address": "string"
  }
}
```

**Output**:
```json
{
  "allowed": "boolean",
  "reason": "string",
  "matched_permissions": ["string"],
  "evaluation_time_ms": "number"
}
```

**Semantics**:
1. Retrieve user's active roles (in specified domain if provided)
2. For each role, collect all permissions (including inherited)
3. Check if any permission matches (resource_type, action)
4. Evaluate any conditions (ABAC)
5. Return decision with audit trail

### 4.2 Role Assignment

**Operation**: `assign_role`

**Input**:
```json
{
  "user_id": "string",
  "role_id": "string",
  "domain": "string|null",
  "granted_by": "string",
  "expires_at": "ISO8601|null"
}
```

**Output**:
```json
{
  "success": "boolean",
  "assignment_id": "string"
}
```

### 4.3 List User Permissions

**Operation**: `list_user_permissions`

**Input**:
```json
{
  "user_id": "string",
  "domain": "string|null",
  "resource_type": "string|null"
}
```

**Output**:
```json
{
  "permissions": [
    {
      "id": "string",
      "resource_type": "string",
      "action": "string",
      "source_role": "string"
    }
  ]
}
```

### 4.4 Batch Authorization

**Operation**: `batch_check`

**Input**:
```json
{
  "checks": [
    {
      "user_id": "string",
      "action": "string",
      "resource": {}
    }
  ]
}
```

**Output**:
```json
{
  "results": [
    {"allowed": "boolean"}
  ]
}
```

---

## 5. Storage Interface

All implementations MUST provide adapters for these storage operations.

### 5.1 Storage Operations

```
Interface: StorageProvider
```

#### Methods

1. **User Operations**
   - `create_user(user: User) -> User`
   - `get_user(user_id: string) -> User | null`
   - `update_user(user: User) -> User`
   - `delete_user(user_id: string) -> boolean`
   - `list_users(filters: object) -> User[]`

2. **Role Operations**
   - `create_role(role: Role) -> Role`
   - `get_role(role_id: string) -> Role | null`
   - `update_role(role: Role) -> Role`
   - `delete_role(role_id: string) -> boolean`
   - `list_roles(filters: object) -> Role[]`

3. **Permission Operations**
   - `create_permission(permission: Permission) -> Permission`
   - `get_permission(permission_id: string) -> Permission | null`
   - `delete_permission(permission_id: string) -> boolean`
   - `list_permissions(filters: object) -> Permission[]`

4. **Assignment Operations**
   - `assign_role(user_id: string, role_id: string, options: object) -> Assignment`
   - `revoke_role(user_id: string, role_id: string, domain: string|null) -> boolean`
   - `get_user_roles(user_id: string, domain: string|null) -> Role[]`
   - `get_role_users(role_id: string) -> User[]`

### 5.2 Storage Backends

Implementations SHOULD support:

- **In-Memory**: For testing and development
- **SQL**: PostgreSQL, MySQL, SQLite
- **NoSQL**: MongoDB, DynamoDB
- **Key-Value**: Redis, Memcached (with persistence)

---

## 6. Wire Format

### 6.1 REST API

**Base URL**: `/api/v1/rbac`

#### Endpoints

```
POST   /check                    # Authorization check
POST   /batch/check              # Batch authorization
GET    /users/:id/permissions    # List user permissions
POST   /users/:id/roles          # Assign role
DELETE /users/:id/roles/:role_id # Revoke role
GET    /roles/:id/permissions    # Get role permissions
POST   /roles                    # Create role
GET    /roles                    # List roles
```

#### Headers

```
Content-Type: application/json
X-API-Version: 1.0
X-Request-ID: <unique-request-id>
Authorization: Bearer <token>
```

#### Response Format

**Success**:
```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "string",
    "timestamp": "ISO8601",
    "version": "1.0"
  }
}
```

**Error**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  },
  "meta": {
    "request_id": "string",
    "timestamp": "ISO8601"
  }
}
```

### 6.2 gRPC (Future)

Protocol Buffer definitions will be provided for high-performance scenarios.

---

## 7. Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `PERMISSION_DENIED` | User lacks required permission | 403 |
| `USER_NOT_FOUND` | User does not exist | 404 |
| `ROLE_NOT_FOUND` | Role does not exist | 404 |
| `INVALID_INPUT` | Input validation failed | 400 |
| `CIRCULAR_DEPENDENCY` | Role hierarchy creates cycle | 400 |
| `MAX_DEPTH_EXCEEDED` | Role hierarchy too deep | 400 |
| `STORAGE_ERROR` | Storage backend error | 500 |
| `INTERNAL_ERROR` | Unexpected internal error | 500 |

---

## 8. Implementation Guidelines

### 8.1 Language Adapters

Each language adapter MUST:

1. **Implement Core Interfaces**
   - Authorization checker
   - Role manager
   - Permission manager
   - Storage provider interface

2. **Provide Idiomatic APIs**
   - Follow language conventions (camelCase vs snake_case)
   - Use native types (Lists, Sets, Maps)
   - Leverage language features (async/await, promises, etc.)

3. **Include Tests**
   - Unit tests (90%+ coverage)
   - Integration tests
   - Performance benchmarks

4. **Documentation**
   - API reference
   - Getting started guide
   - Code examples

### 8.2 Reference Implementations

**Priority Order**:
1. **Python** (reference implementation)
2. **Node.js/TypeScript** (web ecosystem)
3. **Go** (cloud-native, performance)
4. **Java** (enterprise)
5. **.NET/C#** (enterprise)

### 8.3 Performance Requirements

- **Simple Check**: < 1ms (in-memory)
- **With Hierarchy**: < 5ms (depth ≤ 5)
- **Batch Check (100)**: < 50ms
- **Throughput**: > 10,000 ops/sec per core

### 8.4 Security Requirements

1. **Default Deny**: All access denied unless explicitly allowed
2. **Input Validation**: All inputs validated against schema
3. **Audit Logging**: All authorization decisions logged
4. **No Information Leakage**: Error messages don't reveal system details
5. **Encryption**: Sensitive data encrypted at rest and in transit

### 8.5 Versioning

- **Protocol Version**: Semantic versioning (MAJOR.MINOR.PATCH)
- **API Version**: URI path versioning (`/v1/`, `/v2/`)
- **Backward Compatibility**: Maintained for at least 2 major versions

---

## 9. Examples

### 9.1 Simple Authorization Check

**Request**:
```json
POST /api/v1/rbac/check
{
  "user_id": "user_123",
  "action": "read",
  "resource": {
    "type": "document",
    "id": "doc_456"
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "allowed": true,
    "reason": "User has 'editor' role with 'document:read' permission",
    "matched_permissions": ["perm_doc_read"],
    "evaluation_time_ms": 2
  }
}
```

### 9.2 Role Assignment

**Request**:
```json
POST /api/v1/rbac/users/user_123/roles
{
  "role_id": "role_editor",
  "domain": "company_a",
  "granted_by": "admin_user",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

---

## 10. Compliance

This protocol is designed to comply with:

- **NIST RBAC Standard** (NIST IR 7316)
- **OWASP Authorization Guidelines**
- **ISO/IEC 27001** (Access Control)
- **GDPR** (Data Protection)

---

## Appendix A: Migration Guide

Guidelines for migrating from other RBAC systems will be provided separately.

## Appendix B: JSON Schema Definitions

Complete JSON Schema files are available in `/schemas/` directory.

---

**Version History**:
- v1.0.0 (2026-01-08): Initial specification
