# RBAC Algorithm - Language Adapter Implementation Plan

**Status**: Planning Phase  
**Date**: January 12, 2026  
**Target Languages**: Java, Go, JavaScript/React  

---

## Executive Summary

This document outlines the strategy for building language adapters for the RBAC Algorithm. The Python implementation serves as the reference, with JSON schemas ensuring protocol consistency across all implementations.

**Current State**:
- ✅ Python (Reference Implementation): Fully functional with 10K+ checks/sec
- ✅ Protocol Specification: Language-agnostic PROTOCOL.md defined
- ✅ JSON Schemas: 5 schemas (user, role, permission, auth-request, auth-response)
- 📝 Documentation: Adapter pages created (under construction)

**Target State**:
- 🎯 Java Adapter: Native Spring Boot integration
- 🎯 Go Adapter: High-performance microservices
- 🔍 JavaScript/React: Evaluate need (REST API may suffice)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│         Protocol Specification (Language Agnostic)       │
│         - JSON Schemas (5 schemas)                       │
│         - REST API (8 endpoints)                         │
│         - Data Models (User, Role, Permission, etc.)     │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┬──────────────┐
            │               │               │              │
┌───────────▼──────────┐ ┌──▼───────────┐ ┌▼──────────┐ ┌▼──────────┐
│   Python Adapter     │ │ Java Adapter │ │ Go Adapter│ │ JS Client │
│   (Reference)        │ │ (Planned)    │ │ (Planned) │ │ (TBD)     │
│   - Native SDK       │ │ - Spring     │ │ - Fiber   │ │ - REST    │
│   - 10K+ checks/sec  │ │ - JPA        │ │ - Chi     │ │ - React   │
└──────────────────────┘ └──────────────┘ └───────────┘ └───────────┘
```

---

## 1. Java Adapter Implementation Plan

### 1.1 Why Java?

**Strategic Rationale**:
- **Enterprise Demand**: Java dominates enterprise backends (Spring Boot, Jakarta EE)
- **Performance**: JVM JIT compilation delivers excellent throughput
- **Ecosystem**: Massive ecosystem (Maven Central, Spring, etc.)
- **Target Users**: Banks, insurance companies, large enterprises

**Use Cases**:
- Spring Boot microservices authorization
- Jakarta EE application security
- Kafka/event-driven authorization decisions
- Large-scale enterprise applications

### 1.2 Technology Stack

```
Language:      Java 17+ (LTS)
Build Tool:    Maven 3.9+ (Gradle optional)
Frameworks:    
  - Spring Boot 3.2+ (optional integration)
  - Jakarta EE 10+ (optional integration)
Storage:       
  - JDBC (PostgreSQL, MySQL)
  - Redis (cache)
  - In-memory (testing)
Testing:       
  - JUnit 5
  - Mockito
  - TestContainers
Performance:   
  - JMH (benchmarking)
  - Micrometer (metrics)
```

### 1.3 Project Structure

```
rbac-algorithm-java/
├── pom.xml                          # Maven configuration
├── README.md                        # Getting started
├── LICENSE                          # MIT
├── CHANGELOG.md                     # Version history
│
├── rbac-core/                       # Core library (no framework dependencies)
│   ├── pom.xml
│   └── src/
│       ├── main/java/dev/rbacalgorithm/
│       │   ├── models/              # Data models
│       │   │   ├── User.java
│       │   │   ├── Role.java
│       │   │   ├── Permission.java
│       │   │   ├── Resource.java
│       │   │   └── RoleAssignment.java
│       │   │
│       │   ├── storage/             # Storage interfaces & implementations
│       │   │   ├── IStorageProvider.java
│       │   │   ├── MemoryStorage.java
│       │   │   ├── JdbcStorage.java
│       │   │   └── RedisStorage.java
│       │   │
│       │   ├── engine/              # Authorization engine
│       │   │   ├── AuthorizationEngine.java
│       │   │   ├── RoleHierarchyResolver.java
│       │   │   └── PolicyEvaluator.java
│       │   │
│       │   ├── cache/               # Caching
│       │   │   ├── ICacheProvider.java
│       │   │   └── CaffeineCache.java
│       │   │
│       │   ├── exceptions/          # Exception types
│       │   │   ├── RBACException.java
│       │   │   ├── PermissionDeniedException.java
│       │   │   └── ValidationException.java
│       │   │
│       │   └── RBAC.java            # Main API class
│       │
│       └── test/java/               # Unit tests
│
├── rbac-spring-boot-starter/        # Spring Boot auto-configuration
│   ├── pom.xml
│   └── src/
│       ├── main/java/dev/rbacalgorithm/spring/
│       │   ├── RBACAutoConfiguration.java
│       │   ├── RBACProperties.java
│       │   └── annotations/
│       │       ├── @RequirePermission.java
│       │       └── @RequireRole.java
│       │
│       └── resources/
│           └── META-INF/
│               └── spring.factories
│
├── rbac-rest-api/                   # REST API server (optional)
│   ├── pom.xml
│   └── src/main/java/dev/rbacalgorithm/api/
│       ├── controllers/
│       ├── dto/
│       └── RBACApiApplication.java
│
└── examples/                        # Example applications
    ├── spring-boot-example/
    ├── jakarta-ee-example/
    └── plain-java-example/
```

### 1.4 Implementation Phases

#### Phase 1: Core Library (Week 1-2)
- [ ] Setup Maven multi-module project
- [ ] Implement data models (User, Role, Permission, Resource)
- [ ] Implement IStorageProvider interface
- [ ] Implement MemoryStorage (for testing)
- [ ] Implement RBAC main class
- [ ] Write unit tests (80%+ coverage)

**Deliverable**: `rbac-core-1.0.0-alpha.jar`

#### Phase 2: Storage Implementations (Week 3)
- [ ] Implement JdbcStorage (PostgreSQL, MySQL)
- [ ] Implement RedisStorage (cache + storage)
- [ ] Add connection pooling (HikariCP)
- [ ] Write integration tests (TestContainers)

**Deliverable**: `rbac-core-1.0.0-beta.jar`

#### Phase 3: Spring Boot Integration (Week 4)
- [ ] Create spring-boot-starter module
- [ ] Implement auto-configuration
- [ ] Create annotations (@RequirePermission, @RequireRole)
- [ ] Add AOP interceptor for method security
- [ ] Write example Spring Boot app

**Deliverable**: `rbac-spring-boot-starter-1.0.0.jar`

#### Phase 4: Performance & Polish (Week 5)
- [ ] Implement Caffeine cache
- [ ] Run JMH benchmarks (target: 50K+ checks/sec)
- [ ] Add Micrometer metrics
- [ ] Write comprehensive documentation
- [ ] Publish to Maven Central

**Deliverable**: `rbac-algorithm-java-1.0.0.jar` (production-ready)

### 1.5 API Design (Java)

```java
// Basic Usage
import dev.rbacalgorithm.RBAC;
import dev.rbacalgorithm.models.*;

public class Example {
    public static void main(String[] args) {
        // Initialize
        RBAC rbac = RBAC.builder()
            .storage(StorageType.MEMORY)
            .cache(CacheConfig.builder()
                .enabled(true)
                .ttl(Duration.ofMinutes(5))
                .build())
            .build();
        
        // Create entities
        User user = rbac.createUser("user_123", "alice@example.com", "Alice");
        Role role = rbac.createRole("role_editor", "Editor", 
            List.of("perm_doc_read", "perm_doc_write"));
        
        // Assign role
        rbac.assignRole("user_123", "role_editor");
        
        // Check permission
        boolean allowed = rbac.can("user_123", "write", "document");
        if (allowed) {
            // Grant access
        }
        
        // Detailed check
        AuthorizationResult result = rbac.checkPermissionDetailed(
            "user_123", "write", "document");
        System.out.println(result.getReason());
    }
}
```

```java
// Spring Boot Integration
import dev.rbacalgorithm.spring.annotations.RequirePermission;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {
    
    @GetMapping("/{id}")
    @RequirePermission(action = "read", resource = "document")
    public Document getDocument(@PathVariable String id) {
        // Only executed if user has permission
        return documentService.findById(id);
    }
    
    @PutMapping("/{id}")
    @RequirePermission(action = "write", resource = "document")
    public Document updateDocument(@PathVariable String id, @RequestBody Document doc) {
        return documentService.update(id, doc);
    }
}
```

### 1.6 Performance Targets

| Metric | Target | How to Achieve |
|--------|--------|----------------|
| Authorization checks/sec | 50,000+ | Caffeine cache, optimized lookups |
| Latency (p99) | < 5ms | In-memory caching, connection pooling |
| Memory overhead | < 100MB | Efficient data structures, cache limits |
| Startup time | < 2s | Lazy initialization, minimal reflection |

---

## 2. Go Adapter Implementation Plan

### 2.1 Why Go?

**Strategic Rationale**:
- **Performance**: Native compilation, goroutines for concurrency
- **Cloud-Native**: Docker, Kubernetes, microservices standard
- **Simplicity**: Easy deployment (single binary), fast startup
- **Target Users**: DevOps teams, API gateways, cloud-native startups

**Use Cases**:
- API gateway authorization (Traefik, Kong)
- Cloud-native microservices (Kubernetes)
- High-throughput authorization services
- CLI tools for RBAC management

### 2.2 Technology Stack

```
Language:      Go 1.21+
Package Mgr:   Go Modules
Frameworks:    
  - Fiber v2 (web framework)
  - Chi v5 (HTTP router)
  - gRPC (optional)
Storage:       
  - PostgreSQL (pgx driver)
  - Redis (go-redis)
  - In-memory (sync.Map)
Testing:       
  - testing (standard library)
  - testify (assertions)
  - dockertest (integration)
Performance:   
  - pprof (profiling)
  - Prometheus (metrics)
```

### 2.3 Project Structure

```
rbac-algorithm-go/
├── go.mod                           # Go modules
├── go.sum
├── README.md
├── LICENSE
├── Makefile                         # Build automation
│
├── pkg/                             # Public API
│   ├── rbac/
│   │   ├── rbac.go                  # Main RBAC interface
│   │   ├── options.go               # Configuration
│   │   └── rbac_test.go
│   │
│   ├── models/                      # Data models
│   │   ├── user.go
│   │   ├── role.go
│   │   ├── permission.go
│   │   └── resource.go
│   │
│   ├── storage/                     # Storage interfaces
│   │   ├── storage.go               # Interface
│   │   ├── memory.go                # In-memory
│   │   ├── postgres.go              # PostgreSQL
│   │   └── redis.go                 # Redis
│   │
│   ├── engine/                      # Authorization engine
│   │   ├── authorizer.go
│   │   ├── hierarchy.go
│   │   └── evaluator.go
│   │
│   └── cache/                       # Caching
│       ├── cache.go
│       └── lru.go
│
├── internal/                        # Private implementation
│   └── utils/
│
├── cmd/                             # CLI tools
│   ├── rbac-server/                 # REST API server
│   │   └── main.go
│   └── rbac-cli/                    # Management CLI
│       └── main.go
│
├── examples/                        # Example applications
│   ├── fiber-example/
│   ├── chi-example/
│   └── basic-example/
│
└── docs/                            # Documentation
    ├── getting-started.md
    └── api-reference.md
```

### 2.4 Implementation Phases

#### Phase 1: Core Library (Week 1-2)
- [ ] Setup Go modules project
- [ ] Implement data models (structs)
- [ ] Implement Storage interface
- [ ] Implement MemoryStorage
- [ ] Implement RBAC main struct
- [ ] Write unit tests (80%+ coverage)

**Deliverable**: `github.com/maneesh-relanto/rbac-algorithm-go v0.1.0`

#### Phase 2: Storage Implementations (Week 3)
- [ ] Implement PostgreSQL storage (pgx)
- [ ] Implement Redis storage + cache
- [ ] Add connection pooling
- [ ] Write integration tests (dockertest)

**Deliverable**: `v0.2.0`

#### Phase 3: Web Framework Integration (Week 4)
- [ ] Create Fiber middleware
- [ ] Create Chi middleware
- [ ] Build REST API server (`cmd/rbac-server`)
- [ ] Write example apps

**Deliverable**: `v0.3.0`

#### Phase 4: Performance & Polish (Week 5)
- [ ] Implement LRU cache
- [ ] Run benchmarks (target: 100K+ checks/sec)
- [ ] Add Prometheus metrics
- [ ] Write comprehensive documentation
- [ ] Tag v1.0.0 release

**Deliverable**: `v1.0.0` (production-ready)

### 2.5 API Design (Go)

```go
// Basic Usage
package main

import (
    "github.com/maneesh-relanto/rbac-algorithm-go/pkg/rbac"
    "github.com/maneesh-relanto/rbac-algorithm-go/pkg/models"
)

func main() {
    // Initialize
    r, err := rbac.New(rbac.Options{
        Storage: rbac.StorageMemory,
        Cache: rbac.CacheConfig{
            Enabled: true,
            TTL:     5 * time.Minute,
        },
    })
    if err != nil {
        panic(err)
    }
    
    // Create entities
    user, _ := r.CreateUser("user_123", "alice@example.com", "Alice")
    role, _ := r.CreateRole("role_editor", "Editor", []string{
        "perm_doc_read", "perm_doc_write",
    })
    
    // Assign role
    r.AssignRole("user_123", "role_editor")
    
    // Check permission
    allowed, err := r.Can("user_123", "write", "document")
    if allowed {
        // Grant access
    }
    
    // Detailed check
    result, _ := r.CheckPermissionDetailed("user_123", "write", "document")
    fmt.Println(result.Reason)
}
```

```go
// Fiber Middleware
package main

import (
    "github.com/gofiber/fiber/v2"
    rbacmiddleware "github.com/maneesh-relanto/rbac-algorithm-go/pkg/middleware/fiber"
)

func main() {
    app := fiber.New()
    
    // Initialize RBAC
    r, _ := rbac.New(rbac.Options{Storage: rbac.StorageMemory})
    
    // Apply middleware
    app.Use(rbacmiddleware.New(rbacmiddleware.Config{
        RBAC: r,
        UserIDHeader: "X-User-ID",
    }))
    
    // Protected routes
    app.Get("/documents/:id", 
        rbacmiddleware.RequirePermission("read", "document"),
        getDocument,
    )
    
    app.Put("/documents/:id",
        rbacmiddleware.RequirePermission("write", "document"),
        updateDocument,
    )
    
    app.Listen(":3000")
}
```

### 2.6 Performance Targets

| Metric | Target | How to Achieve |
|--------|--------|----------------|
| Authorization checks/sec | 100,000+ | Goroutines, LRU cache, zero-copy |
| Latency (p99) | < 2ms | In-memory caching, sync.Map |
| Memory overhead | < 50MB | Efficient structs, pooling |
| Startup time | < 500ms | Fast Go runtime, minimal init |
| Binary size | < 20MB | Go compilation, upx compression |

---

## 3. JavaScript/React Evaluation

### 3.1 Current Analysis

**Question**: Do we need a JavaScript adapter, or is REST API sufficient?

**Scenarios to Evaluate**:

1. **Frontend React Apps** (Client-Side)
   - ❌ **Do NOT implement client-side RBAC SDK**
   - ✅ **Use REST API from backend** (backend enforces authorization)
   - **Reason**: Security - never trust client-side authorization

2. **Node.js Backend** (Server-Side)
   - ✅ **Consider building Node.js SDK**
   - **Use Case**: Express, Nest.js, Fastify backends
   - **Alternative**: Use REST API server (Java/Go RBAC microservice)

3. **React UI Components** (Display Logic)
   - ✅ **Build React hooks for UI visibility**
   - **Use Case**: Show/hide buttons based on permissions
   - **Implementation**: Fetch permissions from backend, use context

### 3.2 Recommended Approach

#### Option A: REST API Only (Recommended for MVP)

**Pros**:
- ✅ No additional maintenance
- ✅ Language-agnostic (any client can use)
- ✅ Already have Python/Java/Go backends
- ✅ Security enforced at API layer

**Cons**:
- ❌ Network latency for every check
- ❌ No local caching

**Implementation**:
```javascript
// Frontend calls backend REST API
async function checkPermission(userId, action, resource) {
    const response = await fetch('/api/rbac/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, action, resource })
    });
    return (await response.json()).allowed;
}
```

#### Option B: Node.js SDK (If High Demand)

**Build if**:
- Many users run Node.js backends
- Need local caching for performance
- Want TypeScript type safety

**Technology Stack**:
```
Language:      TypeScript 5+
Package Mgr:   npm/yarn/pnpm
Runtime:       Node.js 18+
Frameworks:    
  - Express (middleware)
  - Nest.js (module)
  - Fastify (plugin)
Storage:       
  - Redis (ioredis)
  - PostgreSQL (pg)
  - In-memory (Map)
Testing:       
  - Jest
  - Supertest
```

**API Design (TypeScript)**:
```typescript
import { RBAC } from 'rbac-algorithm';

const rbac = new RBAC({
  storage: 'memory',
  cache: { enabled: true, ttl: 300 }
});

// Express middleware
import { requirePermission } from 'rbac-algorithm/express';

app.get('/documents/:id', 
  requirePermission('read', 'document'),
  (req, res) => {
    res.json({ document: 'content' });
  }
);

// React hooks
import { useRBAC } from 'rbac-algorithm/react';

function DocumentEditor() {
  const { can } = useRBAC();
  const canEdit = can('write', 'document');
  
  return (
    <div>
      {canEdit && <button>Edit</button>}
    </div>
  );
}
```

#### Option C: React Hooks Library (UI Only)

**Purpose**: Show/hide UI elements based on permissions

**NOT** for authorization (backend enforces)

**Implementation**:
```typescript
// packages/rbac-react/src/RBACProvider.tsx
import React, { createContext, useContext } from 'react';

interface RBACContextType {
  permissions: Record<string, boolean>;
  can: (action: string, resource: string) => boolean;
}

const RBACContext = createContext<RBACContextType | null>(null);

export function RBACProvider({ children, permissions }) {
  const can = (action, resource) => {
    return permissions[`${resource}:${action}`] ?? false;
  };
  
  return (
    <RBACContext.Provider value={{ permissions, can }}>
      {children}
    </RBACContext.Provider>
  );
}

export function useRBAC() {
  return useContext(RBACContext);
}

// Usage
function App() {
  const [permissions, setPermissions] = useState({});
  
  useEffect(() => {
    // Fetch from backend
    fetch('/api/rbac/permissions').then(r => r.json()).then(setPermissions);
  }, []);
  
  return (
    <RBACProvider permissions={permissions}>
      <Dashboard />
    </RBACProvider>
  );
}

function Dashboard() {
  const { can } = useRBAC();
  
  return (
    <div>
      {can('read', 'document') && <ViewButton />}
      {can('write', 'document') && <EditButton />}
      {can('delete', 'document') && <DeleteButton />}
    </div>
  );
}
```

### 3.3 Final Recommendation for JavaScript

**Phase 1 (Now - Q1 2026)**:
- ✅ **REST API only** - Use Java/Go backend
- ✅ **Document REST API** usage in docs
- ✅ **Provide JavaScript examples** (fetch calls)
- ❌ **Skip Node.js SDK** (wait for demand)

**Phase 2 (Q2 2026 - If Demand Exists)**:
- Build lightweight React hooks library (`rbac-react`)
- Publish to npm as `@rbac-algorithm/react`
- NO full Node.js SDK yet

**Phase 3 (Q3 2026 - If High Demand)**:
- Build full Node.js/TypeScript SDK
- Publish to npm as `rbac-algorithm`
- Include Express, Nest.js, Fastify integrations

---

## 4. Implementation Priorities

### Q1 2026 (Jan-Mar)
1. **Java Adapter** - High Priority
   - Weeks 1-5: Build core + Spring Boot starter
   - Week 6: Publish to Maven Central
   - Week 7-8: Documentation + examples

2. **Go Adapter** - High Priority
   - Weeks 1-5: Build core + middleware
   - Week 6: Tag v1.0.0 release
   - Week 7-8: Documentation + examples

3. **JavaScript** - Low Priority (Documentation Only)
   - Week 1: Document REST API usage
   - Week 2: Add JavaScript fetch examples to docs

### Q2 2026 (Apr-Jun)
- React hooks library (if user requests)
- Performance optimizations
- Additional storage backends (MongoDB, DynamoDB)

### Q3 2026 (Jul-Sep)
- Node.js SDK (if high demand)
- gRPC protocol support
- C# adapter (if enterprise demand)

---

## 5. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Adoption** |
| GitHub stars | 1,000+ | GitHub API |
| Maven downloads | 10,000+/month | Maven Central stats |
| Go pkg.go.dev views | 5,000+/month | pkg.go.dev analytics |
| **Performance** |
| Java throughput | 50K+ checks/sec | JMH benchmarks |
| Go throughput | 100K+ checks/sec | Go benchmarks |
| **Quality** |
| Test coverage | 80%+ | JaCoCo, go test -cover |
| Documentation | 100% API docs | Javadoc, godoc |
| **Community** |
| Contributors | 10+ | GitHub insights |
| Issues resolved | < 7 days avg | GitHub metrics |

---

## 6. Resource Requirements

### Team
- **Java Developer**: 1 FTE for 2 months
- **Go Developer**: 1 FTE for 2 months
- **Technical Writer**: 0.5 FTE for 1 month

### Infrastructure
- **CI/CD**: GitHub Actions (free for public repos)
- **Package Hosting**: Maven Central (free), pkg.go.dev (free)
- **Documentation**: GitHub Pages (existing)

### Budget
- **Maven Central setup**: $0 (free for OSS)
- **Domain (optional)**: $12/year (rbac-algorithm.dev)
- **Total**: < $100

---

## 7. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Protocol changes break adapters | High | Version all APIs, use semantic versioning |
| Performance doesn't meet targets | Medium | Benchmark early, optimize incrementally |
| Low adoption | Low | Focus on Java first (highest demand) |
| Maintenance burden | Medium | Keep adapters simple, share protocol tests |

---

## 8. Next Steps

### Immediate Actions (This Week)
1. ✅ **Approve this plan** - Review with stakeholders
2. [ ] **Create GitHub repos**:
   - `rbac-algorithm-java`
   - `rbac-algorithm-go`
3. [ ] **Setup CI/CD** - GitHub Actions workflows
4. [ ] **Assign developers** - Find Java + Go contributors

### Week 1
1. [ ] Setup Maven multi-module project (Java)
2. [ ] Setup Go modules project (Go)
3. [ ] Implement data models (both)
4. [ ] Start unit tests (both)

### Week 2
1. [ ] Implement storage interfaces
2. [ ] Implement MemoryStorage
3. [ ] Implement main RBAC class
4. [ ] Continue tests (target: 50%+ coverage)

---

## Appendix A: Protocol Compatibility Matrix

| Feature | Python | Java | Go | JavaScript |
|---------|--------|------|----|-----------||
| Core RBAC | ✅ | 🎯 Planned | 🎯 Planned | ❌ REST API |
| Role Hierarchy | ✅ | 🎯 Planned | 🎯 Planned | ❌ |
| ABAC | ✅ | 🎯 Planned | 🎯 Planned | ❌ |
| Multi-Tenancy | ✅ | 🎯 Planned | 🎯 Planned | ❌ |
| Caching | ✅ | 🎯 Planned | 🎯 Planned | ❌ |
| Audit Logging | ✅ | 🎯 Planned | 🎯 Planned | ❌ |
| REST API | ❌ | 🎯 Planned | 🎯 Planned | ✅ Use Only |
| JSON Schemas | ✅ | ✅ | ✅ | ✅ |

---

## Appendix B: Comparison with Existing Solutions

### Java Space
| Solution | Pros | Cons | Our Advantage |
|----------|------|------|---------------|
| Spring Security | Mature, integrated | Complex, opinionated | Simpler API, multi-framework |
| Apache Shiro | Lightweight | Limited features | More features (ABAC, hierarchy) |
| Keycloak | Full IAM | Heavy, requires server | Embedded library |

### Go Space
| Solution | Pros | Cons | Our Advantage |
|----------|------|------|---------------|
| Casbin | Feature-rich | Complex policy syntax | Simpler API, better docs |
| OPA (Rego) | Powerful | Steep learning curve | Easier integration |
| Go-Guardian | Simple | Basic RBAC only | ABAC + hierarchy |

---

**Document Version**: 1.0  
**Last Updated**: January 12, 2026  
**Owner**: RBAC Algorithm Team  
**Status**: Draft - Awaiting Approval
