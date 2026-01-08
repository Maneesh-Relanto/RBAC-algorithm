# RBAC Algorithm - Quick Reference Card

## 📁 Where to Find Everything

```
Root Files (Essential Only)
├── README.md                    Main documentation
├── LICENSE                      MIT License  
├── .gitignore                   Git rules
├── requirements.txt             Production dependencies
├── setup.py                     Package install
└── PROJECT_STRUCTURE.md         This guide

.quality/                        Code Quality & Analysis
├── sonarqube/                   SonarQube configuration
│   ├── sonar-project.properties 
│   ├── sonar-scan.bat          Run analysis (Windows)
│   └── sonar-scan.sh           Run analysis (Unix)
├── .pylintrc                    Pylint config
├── pyproject.toml               All tool configs
└── requirements-dev.txt         Dev dependencies

scripts/                         Utility Scripts
├── validate-code.bat           Quality check (Windows)
├── validate-code.sh            Quality check (Unix)
├── start-docs.bat              Start docs (Windows)
└── start-docs.sh               Start docs (Unix)

docs/                            Documentation
├── CONTRIBUTING.md             How to contribute
├── FIX_SUMMARY.md             SonarQube fixes
├── TESTING.md                 Testing guide
└── [Docusaurus website]       Interactive docs
```

## ⚡ Quick Commands

### Development
```bash
# Check code quality (run before commit)
.\scripts\validate-code.bat      # Windows
./scripts/validate-code.sh       # Unix

# Start documentation website
.\scripts\start-docs.bat         # Windows
./scripts/start-docs.sh          # Unix

# Run tests
pytest tests/

# Run specific test file
pytest tests/test_models.py
```

### Code Quality
```bash
# Format code
black src tests

# Check types
mypy src

# Lint code
pylint src

# Security scan
bandit -r src
```

### SonarQube
```bash
# Full analysis
.\.quality\sonarqube\sonar-scan.bat  # Windows
./.quality/sonarqube/sonar-scan.sh   # Unix
```

### Installation
```bash
# Install production dependencies
pip install -r requirements.txt

# Install dev dependencies (testing, linting, etc.)
pip install -r .quality/requirements-dev.txt

# Install package in editable mode
pip install -e .
```

## 🎯 Common Tasks

| Task | Command |
|------|---------|
| Run all quality checks | `.\scripts\validate-code.bat` |
| Start docs locally | `.\scripts\start-docs.bat` → http://localhost:3001 |
| Run tests with coverage | `pytest --cov=src tests/` |
| Format code | `black src tests` |
| Check for security issues | `bandit -r src` |
| Run SonarQube analysis | `.\.quality\sonarqube\sonar-scan.bat` |

## 📖 Documentation Locations

| Document | Path |
|----------|------|
| Main README | `README.md` |
| Project Structure | `PROJECT_STRUCTURE.md` |
| Contributing Guide | `docs/CONTRIBUTING.md` |
| Testing Guide | `docs/TESTING.md` |
| Fix Summary | `docs/FIX_SUMMARY.md` |
| Interactive Docs | Run `start-docs` → http://localhost:3001 |

## 🔧 Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `pyproject.toml` | Python tools config | `.quality/pyproject.toml` |
| `.pylintrc` | Pylint settings | `.quality/.pylintrc` |
| `sonar-project.properties` | SonarQube config | `.quality/sonarqube/` |
| `pytest.ini` | Pytest config | In `pyproject.toml` |
| `requirements.txt` | Prod dependencies | Root |
| `requirements-dev.txt` | Dev dependencies | `.quality/` |

## 🎨 Code Style

- **Formatter**: Black (line length: 100)
- **Import sorting**: isort
- **Linter**: Pylint
- **Type checker**: MyPy
- **Security**: Bandit
- **Style guide**: Flake8

All configured in `.quality/pyproject.toml`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_models.py::test_user_creation

# Run with verbose output
pytest -v

# See coverage report
# Opens htmlcov/index.html
```

## 📦 Package Structure

```python
from rbac import RBAC

# Main class
rbac = RBAC()

# Models
from rbac.core.models import User, Role, Permission, Resource

# Storage providers
from rbac.storage import MemoryStorage

# Engine components
from rbac.engine import AuthorizationEngine
```

## 🐛 Troubleshooting

### Scripts not working?
```bash
# Make sure you're in the project root directory
# (The folder containing README.md, src/, docs/, etc.)
cd path/to/rbac-algorithm

# Then run scripts with relative path
.\scripts\validate-code.bat     # Windows
./scripts/validate-code.sh      # Unix/Mac
```

### Import errors in tests?
```bash
# Install package in editable mode
pip install -e .
```

### Quality checks failing?
```bash
# Auto-fix formatting
black src tests

# Auto-fix imports
isort src tests
```

## 🔗 Useful Links

- **Local Docs**: http://localhost:3001 (after running start-docs)
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Testing Guide**: `docs/TESTING.md`
- **Contributing**: `docs/CONTRIBUTING.md`

---

**💡 Pro Tip**: Keep this file open in a separate tab while working!

**🎯 Before Every Commit**: Run `.\scripts\validate-code.bat` to ensure code quality.

**📚 Need Help?**: Check `PROJECT_STRUCTURE.md` for detailed documentation.
