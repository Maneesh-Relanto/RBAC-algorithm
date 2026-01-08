# Project Structure

## Architecture Diagram

![RBAC Architecture](../../docs/static/img/architecture-diagram.svg)

*[Edit diagram in draw.io](../../docs/static/img/architecture-diagram.drawio) - Open with [diagrams.net](https://app.diagrams.net/)*

This document outlines the directory structure and organization principles for the RBAC Algorithm project.

## Directory Layout

```
rbac-algorithm/
├── docs/                           # Documentation
│   ├── getting-started.md         # Quick start guide
│   ├── core-concepts.md           # Core RBAC concepts
│   ├── api-reference.md           # Complete API documentation
│   ├── architecture.md            # System architecture
│   ├── performance.md             # Performance tuning guide
│   ├── security.md                # Security best practices
│   ├── migration.md               # Migration from other systems
│   ├── examples/                  # Code examples
│   └── images/                    # Diagrams and screenshots
│
├── src/                           # Source code
│   ├── core/                      # Core RBAC engine
│   │   ├── models/               # Data models
│   │   │   ├── user.py           # User/Subject model
│   │   │   ├── role.py           # Role model
│   │   │   ├── permission.py     # Permission model
│   │   │   ├── resource.py       # Resource model
│   │   │   └── policy.py         # Policy model
│   │   │
│   │   ├── managers/             # Business logic managers
│   │   │   ├── user_manager.py   # User management
│   │   │   ├── role_manager.py   # Role management
│   │   │   ├── permission_manager.py
│   │   │   └── policy_manager.py
│   │   │
│   │   ├── engine/               # Authorization engine
│   │   │   ├── decision_engine.py
│   │   │   ├── policy_evaluator.py
│   │   │   └── hierarchy_resolver.py
│   │   │
│   │   └── interfaces/           # Abstract interfaces
│   │       ├── storage.py        # Storage interface
│   │       ├── cache.py          # Cache interface
│   │       └── audit.py          # Audit interface
│   │
│   ├── storage/                   # Storage implementations
│   │   ├── memory/               # In-memory storage
│   │   ├── sql/                  # SQL storage (PostgreSQL, MySQL)
│   │   ├── nosql/                # NoSQL storage (MongoDB)
│   │   └── redis/                # Redis storage
│   │
│   ├── cache/                     # Caching layer
│   │   ├── memory_cache.py
│   │   ├── redis_cache.py
│   │   └── cache_strategy.py
│   │
│   ├── audit/                     # Audit logging
│   │   ├── audit_logger.py
│   │   └── formatters/
│   │
│   ├── api/                       # API layer
│   │   ├── rest/                 # REST API
│   │   └── grpc/                 # gRPC API (future)
│   │
│   ├── utils/                     # Utility functions
│   │   ├── validators.py
│   │   ├── serializers.py
│   │   └── exceptions.py
│   │
│   └── config/                    # Configuration
│       ├── settings.py
│       └── defaults.py
│
├── tests/                         # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── performance/              # Performance benchmarks
│   └── fixtures/                 # Test data
│
├── examples/                      # Example implementations
│   ├── basic/                    # Basic usage
│   ├── advanced/                 # Advanced patterns
│   ├── frameworks/               # Framework integrations
│   │   ├── django/
│   │   ├── flask/
│   │   ├── fastapi/
│   │   └── express/
│   └── use-cases/                # Real-world scenarios
│
├── scripts/                       # Utility scripts
│   ├── setup.py                  # Setup scripts
│   ├── benchmark.py              # Performance benchmarking
│   └── migrate.py                # Migration tools
│
├── config/                        # Configuration files
│   ├── config.yaml.example
│   └── docker-compose.yml
│
├── .github/                       # GitHub specific
│   ├── workflows/                # CI/CD pipelines
│   └── ISSUE_TEMPLATE/
│
├── README.md                      # Project overview
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                        # MIT License
├── CHANGELOG.md                  # Version history
├── CODE_OF_CONDUCT.md           # Code of conduct
├── SECURITY.md                   # Security policy
├── requirements.txt              # Python dependencies
├── setup.py                      # Python package setup
└── pyproject.toml               # Python project config
```

## Design Principles

### 1. Separation of Concerns
- **Models**: Pure data structures with minimal logic
- **Managers**: Business logic and orchestration
- **Engine**: Core authorization algorithms
- **Storage**: Data persistence abstraction
- **API**: External interface layer

### 2. Dependency Direction
```
API → Managers → Engine → Models
         ↓          ↓
     Storage    Cache
```

### 3. Interface-Based Design
All storage, cache, and audit implementations follow abstract interfaces for:
- Easy testing with mocks
- Plugin architecture
- Swappable implementations

### 4. Naming Conventions

#### Files
- Snake case: `user_manager.py`
- Descriptive names: `policy_evaluator.py`

#### Classes
- Pascal case: `UserManager`
- Noun-based: `DecisionEngine`

#### Functions/Methods
- Snake case: `check_permission()`
- Verb-based: `assign_role()`

#### Constants
- Upper case: `MAX_HIERARCHY_DEPTH`

### 5. Module Organization

Each module should contain:
```python
"""
Module docstring explaining purpose.
"""

# Standard library imports
import os
import sys

# Third-party imports
import numpy as np

# Local imports
from rbac.core.models import User

# Constants
MAX_RETRIES = 3

# Classes and functions
class MyClass:
    pass
```

### 6. Documentation Standards

#### Code Documentation
- Docstrings for all public classes and methods
- Type hints for all function signatures
- Inline comments for complex logic

#### API Documentation
- OpenAPI/Swagger for REST APIs
- Protocol Buffers for gRPC
- Auto-generated reference docs

### 7. Testing Organization
```
tests/
├── unit/
│   └── core/
│       └── test_user_manager.py
├── integration/
│   └── test_complete_flow.py
└── performance/
    └── benchmark_authorization.py
```

Test file names: `test_<module_name>.py`

### 8. Configuration Management

- Environment-based configuration
- Sensible defaults
- Easy overrides via:
  - Environment variables
  - Config files (YAML/JSON)
  - Code-based configuration

### 9. Security Considerations

- No secrets in code
- Input validation at boundaries
- Secure defaults (deny by default)
- Regular dependency updates

### 10. Performance Guidelines

- Lazy loading where appropriate
- Connection pooling for databases
- Efficient caching strategies
- Batch operations support

## File Headers

All source files should include:

```python
"""
Module Name: Short description

This module provides...

Classes:
    ClassName: Brief description

Functions:
    function_name: Brief description

License:
    MIT License - see LICENSE file
"""
```

## Import Order

1. Standard library imports
2. Related third-party imports
3. Local application imports

```python
# Standard library
import os
from typing import List

# Third-party
import redis

# Local
from rbac.core.models import User
```

## Version Control

- Feature branches: `feature/add-grpc-support`
- Bug fixes: `fix/cache-invalidation`
- Hotfixes: `hotfix/security-patch`
- Releases: `release/v1.0.0`

## Release Process

1. Update CHANGELOG.md
2. Bump version in setup.py
3. Create git tag
4. Build and publish package
5. Update documentation

---

This structure follows industry best practices while remaining flexible for future enhancements.
