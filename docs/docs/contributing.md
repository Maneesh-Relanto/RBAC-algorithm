---
sidebar_position: 100
---

# Contributing to RBAC Algorithm

Thank you for your interest in contributing! This guide will help you get started.

## Ways to Contribute

- 🐛 **Report bugs** - Help us identify and fix issues
- 💡 **Suggest features** - Share ideas for improvements
- 📝 **Improve documentation** - Fix typos, add examples, clarify concepts
- 💻 **Submit code** - Bug fixes, features, tests
- 🌐 **Add language adapters** - Implement protocol in new languages

## Getting Started

### 1. Fork & Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/RBAC-algorithm.git
cd RBAC-algorithm
```

### 2. Set Up Development Environment

```bash
# Create virtual environment (Python)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package in editable mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black isort mypy
```

### 3. Verify Setup

```bash
# Run tests to ensure everything works
pytest tests/

# Run benchmarks
python benchmarks/quick_benchmark.py

# Check code quality baselines
ls repo-health/baseline/
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Guidelines

### Code Style

We follow industry-standard code styles:

**Python:**
- PEP 8 compliant
- Type hints for all functions
- Docstrings (Google style)
- Black formatter
- isort for imports

```python
def check_permission(
    self,
    user_id: str,
    action: str,
    resource_id: str,
    *,
    domain: Optional[str] = None
) -> AuthorizationResult:
    """Check if user has permission to perform action.
    
    Args:
        user_id: Unique identifier of the user
        action: Action to perform (read, write, delete, etc.)
        resource_id: Unique identifier of the resource
        domain: Optional domain for multi-tenancy
        
    Returns:
        AuthorizationResult with allowed status and details
        
    Raises:
        UserNotFoundError: If user doesn't exist
        ResourceNotFoundError: If resource doesn't exist
    """
    pass
```

**JavaScript:**
- ESLint + Prettier
- JSDoc comments
- ES6+ features

### Testing

All code must include tests:

```bash
# Run tests
pytest

# With coverage
pytest --cov=rbac --cov-report=html

# Run specific test
pytest tests/test_rbac.py::TestRBAC::test_check_permission
```

**Test Requirements:**
- Unit tests for new functions
- Integration tests for workflows
- Edge cases covered
- Maintain 95%+ coverage (current baseline)

### Code Quality

We maintain A-grade code quality standards:

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Check against quality baselines
cat repo-health/baseline/sonarqube-baseline.md
cat repo-health/baseline/coverage-baseline.txt

# Run benchmarks to verify performance
python benchmarks/quick_benchmark.py
```

**Quality Requirements:**
- ✅ Zero bugs (SonarQube verified)
- ✅ Zero security vulnerabilities
- ✅ Test coverage ≥95%
- ✅ Code quality grade A
- ✅ Cognitive complexity <15 per function

See [repo-health/](https://github.com/Maneesh-Relanto/RBAC-algorithm/tree/main/repo-health) for baseline metrics.

### Documentation

Update documentation when you:
- Add new features
- Change APIs
- Fix bugs that affect usage

```bash
# Build docs locally
cd docs
npm install
npm start
```

## Pull Request Process

### 1. Before Submitting

- ✅ Tests pass locally (`pytest tests/`)
- ✅ Code formatted (black, isort)
- ✅ Coverage maintained (≥95%)
- ✅ Benchmarks pass (no performance regression)
- ✅ Documentation updated
- ✅ Commit messages clear
- ✅ No merge conflicts

### 2. Create Pull Request

**Title Format:**
- `feat: Add role hierarchy visualization`
- `fix: Resolve circular dependency detection bug`
- `docs: Update ABAC examples`
- `test: Add integration tests for multi-tenancy`

**Description Template:**
```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### 3. Code Review

- Address reviewer feedback
- Keep discussion constructive
- Update based on suggestions
- Don't take it personally - we're all learning!

### 4. Merge

Once approved, maintainers will merge your PR.

## Development Workflow

### Adding a New Feature

1. **Discuss first** - Open an issue to discuss
2. **Design** - Write design doc for large features
3. **Implement** - Write code + tests
4. **Document** - Update docs
5. **Submit** - Create PR

### Fixing a Bug

1. **Reproduce** - Write failing test
2. **Fix** - Make test pass
3. **Verify** - Ensure no regressions
4. **Document** - Update if needed
5. **Submit** - Create PR

### Adding Language Adapter

1. **Protocol compliance** - Implement all protocols
2. **Idiomatic** - Follow language conventions
3. **Tests** - Comprehensive test suite
4. **Docs** - Language-specific guide
5. **Examples** - Working code samples

## Project Structure

```
rbac-algorithm/
├── src/rbac/                  # Python implementation
│   ├── core/                  # Core models and protocols
│   ├── storage/               # Storage implementations
│   ├── engine/                # Authorization engine
│   └── rbac.py                # Main API
├── tests/                     # Test suite
├── docs/                      # Documentation site
├── examples/                  # Example applications
├── ARCHITECTURE.md            # Architecture documentation
├── PROTOCOL.md                # Protocol specifications
└── README.md                  # Project overview
```

## Coding Conventions

### Python

```python
# Good
def get_user_permissions(user_id: str) -> List[Permission]:
    """Get all permissions for a user."""
    pass

# Bad
def get_perms(uid):
    pass
```

### Naming

- **Functions**: `verb_noun()` - `check_permission()`, `get_user_roles()`
- **Classes**: `PascalCase` - `AuthorizationEngine`, `MemoryStorage`
- **Constants**: `UPPER_SNAKE_CASE` - `DEFAULT_TIMEOUT`, `MAX_RETRIES`
- **Private**: `_prefix` - `_validate_user()`, `_cache`

### Error Handling

```python
# Good - Specific exceptions
raise UserNotFoundError(f"User {user_id} does not exist")

# Bad - Generic exceptions
raise Exception("User not found")
```

### Type Hints

```python
# Always use type hints
def check_permission(
    self,
    user_id: str,
    action: str,
    resource_id: str
) -> AuthorizationResult:
    pass
```

## Communication

### GitHub Issues

- Search existing issues first
- Use issue templates
- Provide reproduction steps for bugs
- Include version information

### Pull Request Reviews

- Be respectful and constructive
- Explain reasoning behind suggestions
- Accept that there are multiple solutions
- Focus on the code, not the person

### Discussions

- Use GitHub Discussions for questions
- Help others when you can
- Share use cases and patterns

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Documentation credits

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

- 💬 [GitHub Discussions](https://github.com/your-org/rbac-algorithm/discussions)
- 📧 Email: contribute@rbac-algorithm.com

Thank you for contributing! 🎉
