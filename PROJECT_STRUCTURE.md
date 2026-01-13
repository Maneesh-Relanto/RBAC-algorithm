# RBAC Algorithm - Project Structure

This document describes the organized project structure and where to find everything.

---

## 📁 Directory Structure

```
RBAC algorithm/
├── 📂 .quality/                    # Code quality & analysis tools
│   ├── 📂 sonarqube/              # SonarQube configuration
│   │   ├── sonar-project.properties
│   │   ├── sonar-scan.bat
│   │   └── sonar-scan.sh
│   ├── .pylintrc                  # Pylint configuration
│   ├── pyproject.toml             # Python project & tool config
│   └── requirements-dev.txt       # Development dependencies
│
├── 📂 docs/                        # Documentation & website
│   ├── 📂 docs/                   # Docusaurus markdown docs
│   ├── 📂 src/                    # React components & pages
│   ├── 📂 static/                 # Static assets (logo, images)
│   ├── CONTRIBUTING.md            # Contribution guidelines
│   ├── FIX_SUMMARY.md            # SonarQube fixes summary
│   ├── TESTING.md                # Testing & QA guide
│   └── docusaurus.config.js      # Docusaurus configuration
│
├── 📂 documentation/               # Original architecture docs
│   └── architecture-diagram.drawio
│
├── 📂 examples/                    # Usage examples
│   ├── basic_usage.py
│   ├── abac_example.py
│   └── ...
│
├── 📂 schemas/                     # JSON schemas
│   └── rbac-schema.json
│
├── 📂 scripts/                     # Utility scripts
│   ├── validate-code.bat         # Code quality check (Windows)
│   ├── validate-code.sh          # Code quality check (Unix)
│   ├── start-docs.bat            # Start docs server (Windows)
│   └── start-docs.sh             # Start docs server (Unix)
│
├── 📂 src/                         # Source code
│   └── 📂 rbac/                   # Main RBAC package
│       ├── 📂 core/               # Core models & protocols
│       ├── 📂 engine/             # Authorization engine
│       ├── 📂 storage/            # Storage providers
│       └── rbac.py               # Main RBAC class
│
├── 📂 tests/                       # Test suite
│   ├── 📂 property/               # Property-based tests (Hypothesis)
│   │   ├── __init__.py
│   │   ├── test_role_invariants.py
│   │   └── test_authorization_invariants.py
│   ├── 📂 integration/            # Integration tests (workflows)
│   │   ├── __init__.py
│   │   └── test_complete_workflows.py
│   ├── conftest.py               # PyTest fixtures & markers
│   ├── test_models.py            # Model unit tests
│   ├── test_storage.py           # Storage unit tests
│   ├── test_rbac.py              # RBAC unit tests
│   ├── test_permissions_matrix.py # Permission matrix tests
│   └── PRIORITY1_README.md       # Priority 1 validation guide
│
├── 📂 scripts/                     # Utility scripts
│   ├── validate-priority1.ps1    # Run all Priority 1 validations (Windows)
│   ├── validate-priority1.sh     # Run all Priority 1 validations (Linux/Mac)
│   ├── scan-vulnerabilities.ps1  # Security vulnerability scanner (Windows)
│   ├── scan-vulnerabilities.sh   # Security vulnerability scanner (Linux/Mac)
│   ├── validate-code.bat/.sh     # Code quality validation
│   └── start-docs.bat/.sh        # Start documentation server
│
├── .gitignore                     # Git ignore rules
├── pytest.ini                     # PyTest configuration (coverage, markers, etc.)
├── LICENSE                        # MIT License
├── README.md                      # Main project readme
├── PRIORITY1_COMPLETE.md          # Priority 1 validation summary
├── requirements.txt               # All dependencies (dev + prod)
└── setup.py                       # Package installation
```

---

## 🎯 Quick Access Guide

### For Development

| Task | Location | Command |
|------|----------|---------|
| **Run code quality checks** | `scripts/validate-code.bat/sh` | `./scripts/validate-code.bat` |
| **Run SonarQube analysis** | `.quality/sonarqube/sonar-scan.bat/sh` | `./.quality/sonarqube/sonar-scan.bat` |
| **Start documentation** | `scripts/start-docs.bat/sh` | `./scripts/start-docs.bat` |
| **View testing guide** | `docs/TESTING.md` | Open in editor |
| **View fix summary** | `docs/FIX_SUMMARY.md` | Open in editor |
| **Configure quality tools** | `.quality/pyproject.toml` | Edit configuration |

### For Contributing

| Document | Location |
|----------|----------|
| **Contribution Guidelines** | `docs/CONTRIBUTING.md` |
| **Code of Conduct** | Check docs/ folder |
| **Testing Guide** | `docs/TESTING.md` |
| **Architecture** | `documentation/architecture-diagram.drawio` |

### For Users

| Resource | Location |
|----------|----------|
| **Getting Started** | `README.md` |
| **Examples** | `examples/` directory |
| **Interactive Docs** | Run `./scripts/start-docs.bat` → http://localhost:3001 |
| **API Reference** | Interactive docs at `/docs/api/` |

---

## 📝 File Categories

### Essential Files (Root)
- `README.md` - Main project documentation
- `LICENSE` - MIT License
- `.gitignore` - Git ignore rules
- `requirements.txt` - Production dependencies
- `setup.py` - Package installation configuration

### Code Quality (`.quality/`)
- **Purpose**: All code quality, testing, and analysis configuration
- **What's inside**: 
  - Pylint, Black, isort, MyPy, Flake8 configs
  - SonarQube project settings
  - Development requirements
- **When to modify**: When adding new quality tools or changing standards

### SonarQube (`.quality/sonarqube/`)
- **Purpose**: SonarQube-specific configuration and scripts
- **What's inside**: 
  - Project properties
  - Analysis scripts for Windows/Unix
- **When to use**: Before committing code, run analysis

### Scripts (`scripts/`)
- **Purpose**: Utility scripts for common tasks
- **What's inside**: 
  - Code validation scripts
  - Documentation server scripts
- **How to use**: Run directly from project root
  ```bash
  # Windows
  .\scripts\validate-code.bat
  
  # Unix/Mac/Linux
  ./scripts/validate-code.sh
  ```

### Documentation (`docs/`)
- **Purpose**: All project documentation and interactive website
- **What's inside**: 
  - Docusaurus website source
  - Markdown documentation
  - React components
  - Logo and static assets
  - Contributing guides
- **How to use**: 
  ```bash
  # Start documentation server
  .\scripts\start-docs.bat  # Windows
  ./scripts/start-docs.sh   # Unix
  ```

---

## 🚀 Common Workflows

### Before Committing Code

1. **Run quality checks**:
   ```bash
   .\scripts\validate-code.bat  # Windows
   ./scripts/validate-code.sh   # Unix
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

3. **Run SonarQube analysis** (optional):
   ```bash
   .\.quality\sonarqube\sonar-scan.bat  # Windows
   ./.quality/sonarqube/sonar-scan.sh   # Unix
   ```

### Viewing Documentation Locally

```bash
# Start the documentation server
.\scripts\start-docs.bat  # Windows
./scripts/start-docs.sh   # Unix

# Open browser to http://localhost:3001
```

### Running Examples

```bash
# From project root
python examples/basic_usage.py
python examples/abac_example.py
```

### Installing Development Tools

```bash
# Install all development dependencies
pip install -r .quality/requirements-dev.txt

# This includes:
# - pytest (testing)
# - black (formatting)
# - pylint (linting)
# - mypy (type checking)
# - flake8 (style guide)
# - bandit (security)
```

---

## 🔧 Configuration Files

### Python Tools (`.quality/pyproject.toml`)
Central configuration for all Python tools:
- pytest
- black
- isort
- mypy
- coverage

### Pylint (`.quality/.pylintrc`)
Pylint-specific configuration with custom rules.

### SonarQube (`.quality/sonarqube/sonar-project.properties`)
SonarQube project settings including:
- Source directories
- Test directories
- Exclusions
- Python version

---

## 📦 Package Structure

```
src/rbac/
├── __init__.py              # Package exports
├── rbac.py                  # Main RBAC class
├── core/                    # Core components
│   ├── models/              # Data models
│   ├── protocols/           # Interfaces
│   └── exceptions/          # Custom exceptions
├── engine/                  # Authorization engine
│   ├── engine.py           # Main engine
│   ├── evaluator.py        # Policy evaluator
│   └── hierarchy.py        # Role hierarchy
└── storage/                 # Storage providers
    ├── base.py             # Base provider
    └── memory.py           # In-memory storage
```

---

## 🎨 Organization Principles

1. **Separation of Concerns**
   - Code quality tools → `.quality/`
   - Documentation → `docs/`
   - Utility scripts → `scripts/`
   - Source code → `src/`
   - Tests → `tests/`

2. **Clean Root Directory**
   - Only essential project files in root
   - Configuration grouped by purpose
   - Easy to navigate and find files

3. **Developer Experience**
   - Scripts in predictable location
   - Clear documentation structure
   - Consistent naming conventions

4. **Maintainability**
   - Related files grouped together
   - Easy to add new tools
   - Clear project boundaries

---

## 📚 Additional Resources

- **Interactive Documentation**: http://localhost:3001 (after running start-docs script)
- **GitHub Repository**: [Your repo URL]
- **PyPI Package**: [Your PyPI URL]
- **Issue Tracker**: [Your issues URL]

---

*Last Updated: January 2026*  
*For questions or suggestions, see `docs/CONTRIBUTING.md`*
