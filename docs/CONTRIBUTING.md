# Contributing to RBAC Algorithm

First off, thank you for considering contributing to RBAC Algorithm! It's people like you that make this project such a great tool for the community.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Process](#development-process)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/rbac-algorithm.git
cd rbac-algorithm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## Development Process

### 1. Fork & Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/rbac-algorithm.git
cd rbac-algorithm

# Add upstream remote
git remote add upstream https://github.com/original/rbac-algorithm.git
```

### 2. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new features
- Update documentation

### 4. Test Your Changes

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Check coverage
pytest --cov=rbac --cov-report=html

# Run linting
flake8 src/
black src/ --check
mypy src/
```

### 5. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with meaningful message
git commit -m "feat: add role hierarchy validation

- Implement depth-first traversal for role chains
- Add circular dependency detection
- Include comprehensive test coverage"
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat(auth): add multi-factor authentication support

fix(cache): resolve Redis connection pool leak

docs(api): update authorization endpoint examples

test(core): add role hierarchy edge cases
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

```python
# Good
def check_permission(user: User, action: str, resource: Resource) -> bool:
    """
    Check if user has permission to perform action on resource.
    
    Args:
        user: The user attempting the action
        action: The action being performed
        resource: The resource being accessed
        
    Returns:
        True if permission granted, False otherwise
        
    Raises:
        ValueError: If user or resource is None
    """
    if user is None or resource is None:
        raise ValueError("User and resource must not be None")
    
    return self._engine.evaluate(user, action, resource)
```

### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Any

def get_user_roles(
    user_id: str, 
    domain: Optional[str] = None
) -> List[Role]:
    """Retrieve all roles for a user."""
    pass
```

### Error Handling

```python
# Good - Specific exceptions
class RBACException(Exception):
    """Base exception for RBAC errors."""
    pass

class PermissionDenied(RBACException):
    """Raised when permission check fails."""
    pass

class RoleNotFound(RBACException):
    """Raised when role doesn't exist."""
    pass

# Usage
def assign_role(user: User, role: Role) -> None:
    if not self._role_exists(role):
        raise RoleNotFound(f"Role {role.name} not found")
```

### Naming Conventions

```python
# Constants
MAX_HIERARCHY_DEPTH = 10
DEFAULT_CACHE_TTL = 300

# Classes
class UserManager:
    pass

class PolicyEvaluator:
    pass

# Functions and methods
def check_permission():
    pass

def get_user_by_id():
    pass

# Private methods
def _validate_input():
    pass

def _build_cache_key():
    pass
```

## Testing Guidelines

### Test Structure

```python
# tests/unit/core/test_user_manager.py

import pytest
from rbac.core.managers import UserManager
from rbac.core.models import User

class TestUserManager:
    """Test suite for UserManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a UserManager instance."""
        return UserManager()
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return User(id="user1", email="test@example.com")
    
    def test_create_user_success(self, manager, sample_user):
        """Test successful user creation."""
        result = manager.create_user(sample_user)
        assert result.id == sample_user.id
        assert result.email == sample_user.email
    
    def test_create_user_duplicate_email(self, manager, sample_user):
        """Test user creation with duplicate email."""
        manager.create_user(sample_user)
        
        with pytest.raises(ValueError, match="Email already exists"):
            manager.create_user(sample_user)
    
    @pytest.mark.parametrize("email,expected", [
        ("valid@example.com", True),
        ("invalid-email", False),
        ("", False),
    ])
    def test_email_validation(self, manager, email, expected):
        """Test email validation with various inputs."""
        result = manager.validate_email(email)
        assert result == expected
```

### Coverage Requirements

- Minimum 90% code coverage for new code
- 100% coverage for critical paths (authorization logic)
- Integration tests for all public APIs

### Performance Tests

```python
# tests/performance/benchmark_authorization.py

import pytest
from rbac import RBAC

@pytest.mark.benchmark
def test_authorization_performance(benchmark):
    """Benchmark authorization check performance."""
    rbac = RBAC()
    # Setup...
    
    result = benchmark(rbac.can, user, "read", resource)
    assert result is True
```

## Documentation

### Code Documentation

```python
class Role:
    """
    Represents a role in the RBAC system.
    
    A role is a named collection of permissions that can be assigned
    to users. Roles support hierarchical relationships through the
    parent attribute.
    
    Attributes:
        id: Unique identifier for the role
        name: Human-readable name
        permissions: List of permissions granted by this role
        parent: Optional parent role for inheritance
        
    Example:
        >>> admin_role = Role(
        ...     id="admin",
        ...     name="Administrator",
        ...     permissions=[read_perm, write_perm]
        ... )
        >>> editor_role = Role(
        ...     id="editor",
        ...     name="Editor",
        ...     parent=admin_role
        ... )
    """
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        permissions: List[Permission] = None,
        parent: Optional['Role'] = None
    ):
        """
        Initialize a Role.
        
        Args:
            id: Unique identifier
            name: Display name for the role
            permissions: List of permissions (default: empty list)
            parent: Parent role for inheritance (default: None)
            
        Raises:
            ValueError: If id or name is empty
        """
        if not id or not name:
            raise ValueError("Role id and name are required")
        
        self.id = id
        self.name = name
        self.permissions = permissions or []
        self.parent = parent
```

### Markdown Documentation

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep it up-to-date

## Pull Request Process

### 1. Update Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

- Use a clear, descriptive title
- Reference related issues
- Describe what changed and why
- Include screenshots for UI changes
- Check all boxes in PR template

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally
```

### 4. Code Review

- Be responsive to feedback
- Make requested changes
- Keep discussions professional and constructive

### 5. Merge

Once approved, a maintainer will merge your PR.

## Community

### Getting Help

- **Documentation**: Check the [docs](docs/) folder
- **Issues**: Browse [existing issues](https://github.com/yourusername/rbac-algorithm/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/yourusername/rbac-algorithm/discussions)
- **Discord**: [Community Discord Server](https://discord.gg/rbac)

### Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

1. Clear description
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment details
5. Code samples

### Feature Requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

1. Problem statement
2. Proposed solution
3. Alternatives considered
4. Use cases

## Recognition

Contributors are recognized in:
- CHANGELOG.md
- README.md contributors section
- Release notes

## Questions?

Feel free to:
- Open an issue
- Start a discussion
- Reach out to maintainers

Thank you for contributing! 🎉
