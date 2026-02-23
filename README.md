# RBAC Algorithm - Enterprise-Grade Authorization Framework

<p align="center">
  <img src="docs/static/img/logo.svg" alt="RBAC Algorithm Logo" width="200" />
</p>

<p align="center">
  <strong>Enterprise Access Control Made Simple</strong>
</p>

<p align="center">
  <a href="https://mthakur-rbac-algorithm.streamlit.app/">🎮 Try Live Demo</a> •
  <a href="#-interactive-documentation">📖 Interactive Docs</a> •
  <a href="#-quick-start">⚡ Quick Start</a> •
  <a href="#-key-features">✨ Features</a> •
  <a href="docs/CONTRIBUTING.md">🤝 Contributing</a>
</p>

<p align="center">
  <a href="https://mthakur-rbac-algorithm.streamlit.app/"><img src="https://img.shields.io/badge/🎮_Live_Demo-Try_Now-blue?style=for-the-badge" alt="Live Demo"></a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <a href="repo-health/baseline/coverage-baseline.txt"><img src="https://img.shields.io/badge/coverage-95%25-brightgreen" alt="Test Coverage"></a>
  <a href="repo-health/baseline/sonarqube-baseline.md"><img src="https://img.shields.io/badge/code%20quality-A-brightgreen" alt="Code Quality"></a>
  <a href="repo-health/baseline/benchmark-baseline.txt"><img src="https://img.shields.io/badge/performance-10K%20checks%2Fsec-orange" alt="Performance"></a>
  <img src="https://img.shields.io/badge/dependencies-0-success" alt="Zero Dependencies">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/tests-121%20passing-brightgreen" alt="121 Tests Passing">
  <img src="https://img.shields.io/badge/property%20tests-Hypothesis-blue" alt="Property Tests">
  <img src="https://img.shields.io/badge/integration%20tests-8-blue" alt="Integration Tests">
  <img src="https://img.shields.io/badge/security%20scan-SonarQube%20%2B%20CodeQL-success" alt="Security Scan">
</p>

## 📖 Interactive Documentation

> **💡 Best Way to Learn!** Our interactive documentation includes live code examples, visual diagrams, and a playground to experiment with RBAC concepts.

### 🚀 One-Click Start

**Windows:**
```bash
.\scripts\start-docs.bat
```

**Linux/Mac:**
```bash
./scripts/start-docs.sh
```

**Manual Start:**
```bash
cd docs
npm install  # First time only
npm start    # Opens at http://localhost:3000
```

**What you'll find:**
- 🎮 **Interactive Playground** - Try RBAC in your browser
- 📊 **Visual Diagrams** - See role hierarchies in action
- 💻 **Code Examples** - Copy-paste ready code in multiple languages
- 🔍 **Full-Text Search** - Find what you need instantly
- 🌓 **Dark Mode** - Easy on the eyes
- 📱 **Mobile Friendly** - Works on any device

### Quick Links to Interactive Docs
Once the server is running, visit:
- **[Home](http://localhost:3000)** - Overview and quick start
- **[Interactive Playground](http://localhost:3000/playground)** - Try it live!
- **[Getting Started](http://localhost:3000/docs/getting-started/installation)** - Step-by-step setup
- **[Concepts](http://localhost:3000/docs/concepts/overview)** - Learn RBAC fundamentals
- **[API Reference](http://localhost:3000/docs/api/overview)** - Complete API docs
- **[Examples](http://localhost:3000/docs/getting-started/first-app)** - Build your first app

---

## Overview

A production-ready, high-performance Role-Based Access Control (RBAC) framework designed for simplicity, excellent developer experience, and enterprise-grade reliability.

## 🏗️ Architecture

![RBAC Architecture](docs/static/img/architecture-diagram.svg)

*✨ Enhanced architecture diagram with colorful icons, clear relationships, and verified accuracy (96%). [View interactive docs](http://localhost:3000/docs/intro) or [edit diagram](docs/static/img/architecture-diagram.drawio) in [diagrams.net](https://app.diagrams.net/).*

## ✨ Key Features

### Core Capabilities
- **🚀 Simple API**: Three-method surface — `can()`, `check()`, `require()`
- **⚡ High Performance**: 10K+ authorization checks/second (benchmarked)
- **🔄 Pluggable Storage**: Protocol-based interface — swap backends without changing app code
- **🏢 Multi-Tenancy**: Domain-scoped users, roles, resources, and assignments
- **📊 Role Hierarchies**: Single-parent inheritance with circular dependency detection
- **🔍 Hybrid RBAC + ABAC**: Dynamic conditions on permissions — ownership, time, level, department
- **🌐 Framework Agnostic**: Works with Flask, FastAPI, or any Python application
- **📦 Zero Core Dependencies**: No external packages required for the core library
- **🎯 Permissions Matrix**: Visual role×permission management with read/edit modes
- **🗄️ SQLAlchemy Adapter**: Built-in support for PostgreSQL, MySQL, SQLite
- **⏱️ Expiring Assignments**: `expires_at` on role assignments — auto-excluded at auth time
- **🚦 User Lifecycle Enforcement**: SUSPENDED/DELETED users denied at engine level automatically

### Validation & Quality
- **🧪 Property-Based Testing**: Adversarial input generation with Hypothesis
- **🔗 Integration Testing**: 8 end-to-end workflow tests covering real-world patterns
- **📈 95%+ Branch Coverage**: 121 tests total — 49 unit + 8 integration + 14 property + 50 SQLAlchemy
- **🔒 Security Scanned**: SonarQube + CodeQL — all findings resolved
- **✅ Dependency Audited**: All Dependabot vulnerabilities resolved

## 🎯 Design Philosophy

1. **Simplicity First**: Easy to understand, easy to implement
2. **Performance**: Sub-millisecond authorization checks
3. **Standards Compliant**: Follows NIST RBAC model and industry best practices
4. **Extensible**: Protocol-based architecture — implement `IStorageProvider` for custom backends
5. **Quality Assured**: Multi-layered automated validation and testing

## 📋 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Maneesh-Relanto/RBAC-algorithm.git
cd RBAC-algorithm

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

Or install from PyPI:

```bash
pip install rbac-algorithm
```

### Basic Usage

```python
from rbac import RBAC

# Initialize RBAC engine (in-memory storage by default)
rbac = RBAC()

# Create a user
user = rbac.create_user(
    user_id="user_john",
    email="john@example.com",
    name="John Doe",
    domain="company_a"
)

# Create permissions
read_perm = rbac.create_permission(
    permission_id="perm_read",
    action="read",
    resource_type="posts"
)

write_perm = rbac.create_permission(
    permission_id="perm_write",
    action="write",
    resource_type="posts"
)

# Create roles with permissions
viewer_role = rbac.create_role(
    role_id="role_viewer",
    name="Viewer",
    domain="company_a",
    permissions=["perm_read"]
)

editor_role = rbac.create_role(
    role_id="role_editor",
    name="Editor",
    domain="company_a",
    permissions=["perm_read", "perm_write"],
    parent_id="role_viewer"   # inherits everything from Viewer
)

# Assign role to user
rbac.assign_role(
    user_id="user_john",
    role_id="role_viewer",
    domain="company_a"
)

# Create a resource
post = rbac.create_resource(
    resource_id="resource_post_1",
    resource_type="posts",
    domain="company_a",
    attributes={"owner_id": "user_john"}
)

# Check permission — simple boolean
if rbac.can("user_john", "read", "posts"):
    print("Access granted!")

# Check permission — with full result details
result = rbac.check("user_john", "read", "posts")
print(f"Allowed: {result['allowed']}")
print(f"Reason:  {result['reason']}")

# Check permission — raises PermissionDenied if denied (for middleware)
rbac.require("user_john", "read", "posts")
```

### Permissions Matrix

Visualize and manage role-permission assignments with an interactive matrix:

```python
from rbac import RBAC, PermissionsMatrixManager, MatrixMode

rbac = RBAC()
matrix_mgr = PermissionsMatrixManager(rbac._storage)

# View current permissions
matrix = matrix_mgr.create_matrix(mode=MatrixMode.READONLY)
matrix_mgr.print_matrix(matrix)

# Output:
# Feature                    |     Viewer      |     Editor      |      Admin
# -------------------------------------------------------------------------------
# document - read            |        Y        |        Y        |        Y
# document - write           |        N        |        Y        |        Y
# document - delete          |        N        |        N        |        Y

# Make changes interactively
editable_matrix = matrix_mgr.create_matrix(mode=MatrixMode.EDITABLE)
matrix_mgr.toggle_permission(editable_matrix, "role_viewer", "perm_write")
matrix_mgr.apply_changes(editable_matrix)  # Persist to storage
```

**Learn more:** See [Permissions Matrix Guide](docs/docs/features/permissions-matrix.md) and [examples/permissions_matrix_example.py](examples/permissions_matrix_example.py)
```

## 📚 Additional Documentation

> **💡 Prefer Markdown?** While we recommend the [interactive documentation](#-interactive-documentation) above, we also maintain markdown docs for offline reading and GitHub browsing.

<details>
<summary><strong>📘 View Markdown Documentation</strong> (Click to expand)</summary>

### Quick Start Guides
- **[Getting Started](documentation/guides/GETTING_STARTED.md)** - Complete introduction to RBAC Algorithm
- **[Quick Start](documentation/guides/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Setup Guide](documentation/guides/SETUP.md)** - Detailed installation and configuration

### Testing & Quality
- **[Testing Guide](docs/TESTING.md)** - Complete testing strategy and tools
- **[Priority 1 Validation](PRIORITY1_COMPLETE.md)** - Advanced validation suite overview
- **[Priority 1 Details](tests/PRIORITY1_README.md)** - Property-based & integration testing guide
- Run all tests: `pytest tests/ -v --cov=src`
- Run Priority 1 validations: `.\scripts\validate-priority1.ps1` (Windows) or `bash scripts/validate-priority1.sh` (Linux/Mac)
- Security scan: `.\scripts\scan-vulnerabilities.ps1` or `bash scripts/scan-vulnerabilities.sh`
- Code quality: `.\scripts\validate-code.bat` (Windows) or `./scripts/validate-code.sh` (Linux/Mac)

### Architecture & Design
- [Architecture Overview](documentation/architecture/ARCHITECTURE.md) - System design and patterns
- [Protocol Specification](documentation/architecture/PROTOCOL.md) - Language-agnostic protocol
- [Project Structure](documentation/architecture/STRUCTURE.md) - Codebase organization
- [Adapter Guidelines](documentation/architecture/ADAPTERS.md) - Multi-language adapters

### Development Resources
- [Deployment Guide](documentation/development/DEPLOYMENT.md) - PyPI & documentation deployment
- [Git Workflow](documentation/development/GIT_GUIDE.md) - Git best practices
- [Implementation Summary](documentation/development/IMPLEMENTATION_SUMMARY.md) - Technical details
- [Contributing](CONTRIBUTING.md) - How to contribute

### Navigation
- [Documentation Index](documentation/README.md) - Browse all markdown documentation

</details>

## 🏗️ Architecture

The RBAC Algorithm follows a layered architecture design:

**Application Layer** → **Authorization API** → **Core RBAC Engine** → **Storage Abstraction**

- **Authorization API**: RBAC class providing simple authorization interface
- **Core RBAC Engine**: User Manager, Role Manager, Permission Manager, Authorization Engine
- **Storage Abstraction**: Protocol-based interface with in-memory implementation

For a detailed visual architecture diagram, see the [Architecture Diagram](#-architecture) section above or visit the [interactive documentation](http://localhost:3000/docs/intro).

## 🎨 Core Concepts

### 1. Subjects (Users/Actors)
Entities that perform actions in the system.

### 2. Roles
Named collection of permissions that can be assigned to users.

### 3. Permissions
Specific rights to perform actions on resources.

### 4. Resources
Objects or entities being accessed (documents, APIs, etc.).

### 5. Policies
Rules that govern access decisions.

## 🚀 Advanced Features

### Role Hierarchies
```python
# Editor inherits all Viewer permissions
rbac.create_role("role_viewer", "Viewer", permissions=["perm_read"])
rbac.create_role("role_editor", "Editor", permissions=["perm_write"], parent_id="role_viewer")
rbac.create_role("role_admin", "Admin", permissions=["perm_delete"], parent_id="role_editor")
# admin → editor → viewer: admin can read, write, and delete
```

### ABAC — Attribute-Based Conditions
```python
# Only allow editing own documents
rbac.create_permission(
    "perm_edit_own", "document", "edit",
    conditions={"resource.owner_id": {"==": "{{user.id}}"}}
)

# Time-gated + level-gated delete
rbac.create_permission(
    "perm_delete_draft", "document", "delete",
    conditions={"user.level": {">": 5}, "resource.status": {"==": "draft"}}
)
```

**12 operators:** `==` `!=` `>` `<` `>=` `<=` `in` `not_in` `contains` `startswith` `endswith` `matches`

### SQLAlchemy Storage (PostgreSQL / MySQL / SQLite)
```python
from rbac.storage.sqlalchemy_adapter import SQLAlchemyStorage

storage = SQLAlchemyStorage("postgresql://user:pass@localhost/mydb")
rbac = RBAC(storage=storage)
```

### Expiring Role Assignments
```python
from datetime import datetime, timedelta, timezone

rbac.assign_role(
    user_id="user_contractor",
    role_id="role_viewer",
    expires_at=datetime.now(timezone.utc) + timedelta(days=30)
)
# Expired assignments are automatically excluded — no cron job needed
```

### User Lifecycle Enforcement
```python
import dataclasses
from rbac.core.models import EntityStatus

# Suspend a user — no access regardless of roles
existing = rbac._storage.get_user("user_john")
rbac._storage.update_user(dataclasses.replace(existing, status=EntityStatus.SUSPENDED))
rbac.can("user_john", "read", "posts")  # False — enforced at engine level
```

### Context-Aware Authorization
```python
rbac.can("user_john", "approve", "invoice", context={
    "amount": 10000,
    "department": "finance"
})
```

## 📊 Performance

- ⚡ **Sub-millisecond authorization checks** (10K+ checks/sec — see `benchmarks/`)
- 🚀 **In-memory storage** for consistent, predictable performance
- 🗄️ **SQLAlchemy storage** for persistent deployments with connection pooling

*See the `benchmarks/` directory for detailed performance results.*

## 🔒 Security

- **Principle of Least Privilege**: Default deny — access requires explicit permission
- **Input Validation**: All entity IDs validated against prefix rules (`user_`, `role_`, `perm_`, `resource_`)
- **No Information Leakage**: Denied results return `False`/`PermissionDenied` without exposing role details
- **User Lifecycle Enforcement**: SUSPENDED and DELETED users are denied at the engine level
- **Dependency Audited**: All Dependabot vulnerabilities resolved; scanned with Safety + pip-audit
- **SonarQube + CodeQL**: All security findings resolved across source and integration layers

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

## 📁 Project Organization

This project follows a clean, organized structure:

```
RBAC algorithm/
├── 📂 .quality/          # Code quality & SonarQube configs
├── 📂 docs/              # Documentation & website
├── 📂 scripts/           # Utility scripts (validate, start-docs)
├── 📂 src/               # Source code
├── 📂 tests/             # Test suite
└── 📂 examples/          # Usage examples
```

**Quick References:**
- 📖 **[Project Structure](PROJECT_STRUCTURE.md)** - Detailed directory guide
- ⚡ **[Quick Reference](QUICK_REFERENCE.md)** - Commands & shortcuts
- 🧪 **[Testing Guide](docs/TESTING.md)** - How to test & validate code
- 🔍 **[Fix Summary](docs/FIX_SUMMARY.md)** - SonarQube fixes documentation
- ✅ **[Priority 1 Validation](PRIORITY1_COMPLETE.md)** - Advanced validation overview

**Common Commands:**
```bash
# Run core test suite (121 tests)
pytest tests/

# Run by type
pytest tests/property/ -m property      # Property-based tests (Hypothesis)
pytest tests/integration/ -m integration # Integration tests
pytest tests/test_sqlalchemy_storage.py  # SQLAlchemy adapter tests

# Run integration apps (run separately to avoid module name collision)
pytest test-apps/02-flask-blog-api/      # Flask Blog API — 34 tests
pytest test-apps/03-fastapi-blog-api/    # FastAPI Blog API — 39 tests

# With coverage (enforces 95% threshold)
pytest tests/ --cov=src --cov-branch

# Code quality check
.\scripts\validate-code.bat           # Windows
./scripts/validate-code.sh            # Unix

# Security vulnerability scan
.\scripts\scan-vulnerabilities.ps1    # Windows
bash scripts/scan-vulnerabilities.sh  # Linux/Mac

# Start documentation
.\scripts\start-docs.bat              # Windows
./scripts/start-docs.sh               # Unix
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by NIST RBAC standard
- Based on patterns from Casbin, Ory Keto, and Oso
- Special thanks to the open-source community

## ️ Production Ready

This library is **battle-tested and production-ready** with:

- ✅ Core RBAC implementation (users, roles, permissions, resources)
- ✅ Multi-tenancy / domain isolation
- ✅ Role hierarchies with permission inheritance and circular dependency detection
- ✅ Hybrid RBAC + ABAC with 12 condition operators
- ✅ User lifecycle enforcement (ACTIVE / SUSPENDED / DELETED)
- ✅ Expiring role assignments (`expires_at` — auto-excluded at runtime)
- ✅ In-memory storage (zero-config, production-speed)
- ✅ SQLAlchemy storage adapter (PostgreSQL, MySQL, SQLite)
- ✅ Permissions matrix for visual role×permission management
- ✅ Flask Blog API integration (34 tests — JWT auth, ownership, admin panel)
- ✅ FastAPI Blog API integration (39 tests — async, dependency injection, Pydantic)
- ✅ Interactive Streamlit demo (live on Streamlit Community Cloud)
- ✅ 121 tests total (49 unit + 8 integration + 14 property-based + 50 SQLAlchemy)
- ✅ 95%+ branch coverage
- ✅ Property-based testing with Hypothesis (adversarial input generation)
- ✅ SonarQube + CodeQL security scan — all findings resolved
- ✅ Zero core dependencies
- ✅ 10K+ authorization checks per second (benchmarked)

---

**Made with ❤️ for developers who value simplicity and performance**
