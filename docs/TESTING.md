# Code Quality & Testing Guide

## Current Status

**Source Code:** 3,913 lines  
**Test Code:** 0 lines → **NOW: 400+ lines** ✅  
**Test Coverage:** 0% → **Target: 80%+** 🎯

## 📊 Code Quality Tools

We've set up comprehensive code quality tooling:

### 1. **Testing Framework**
- **pytest** - Modern testing framework
- **pytest-cov** - Coverage reporting
- **pytest-benchmark** - Performance testing
- **pytest-mock** - Mocking support

### 2. **Code Formatting**
- **Black** - Opinionated code formatter (100 char line length)
- **isort** - Import statement organizer

### 3. **Static Analysis**
- **Pylint** - Comprehensive code analyzer
- **Flake8** - Style guide enforcement
- **MyPy** - Static type checker

### 4. **Security**
- **Bandit** - Security issue scanner
- **Safety** - Dependency vulnerability checker

## 🚀 Quick Start

### Install Development Dependencies

```bash
# Windows
.\venv\Scripts\activate
pip install -r requirements-dev.txt

# Linux/Mac
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Run All Quality Checks

```bash
# Windows
.\validate-code.bat

# Linux/Mac
chmod +x validate-code.sh
./validate-code.sh
```

This runs:
1. Black (formatter check)
2. isort (import sorting)
3. Pylint (code analysis)
4. Flake8 (style guide)
5. MyPy (type checking)
6. Bandit (security)
7. PyTest (unit tests + coverage)

## 📝 Running Individual Tools

### Format Code
```bash
# Check formatting
black --check src tests

# Auto-format
black src tests

# Sort imports
isort src tests
```

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src/rbac --cov-report=html

# Specific test file
pytest tests/test_models.py

# Specific test
pytest tests/test_models.py::TestUser::test_create_user

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Code Analysis
```bash
# Pylint (full analysis)
pylint src

# Flake8 (style guide)
flake8 src tests --max-line-length=100

# MyPy (type checking)
mypy src

# Bandit (security)
bandit -r src
```

## 🔍 SonarQube Integration

### Setup SonarQube

#### Option 1: Docker (Recommended)
```bash
# Start SonarQube
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest

# Wait for startup (1-2 minutes)
# Access: http://localhost:9000
# Default credentials: admin/admin
```

#### Option 2: Local Installation
1. Download from: https://www.sonarsource.com/products/sonarqube/downloads/
2. Extract and run: `bin/windows-x86-64/StartSonar.bat` (Windows) or `bin/linux-x86-64/sonar.sh start` (Linux)

### Generate Authentication Token

1. Go to http://localhost:9000
2. Log in (admin/admin)
3. Go to: **My Account → Security → Generate Token**
4. Save your token

### Set Environment Variables

```bash
# Windows (PowerShell)
$env:SONAR_HOST_URL = "http://localhost:9000"
$env:SONAR_TOKEN = "your-token-here"

# Linux/Mac
export SONAR_HOST_URL="http://localhost:9000"
export SONAR_TOKEN="your-token-here"
```

### Run SonarQube Analysis

```bash
# Windows
.\sonar-scan.bat

# Linux/Mac
chmod +x sonar-scan.sh
./sonar-scan.sh
```

### View Results

1. Go to: http://localhost:9000/dashboard?id=rbac-algorithm
2. Review:
   - **Bugs** - Logic errors
   - **Vulnerabilities** - Security issues
   - **Code Smells** - Maintainability issues
   - **Coverage** - Test coverage
   - **Duplications** - Code duplication

## 📈 Test Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Models | 100% | 0% → Tests created ✅ |
| Storage | 90%+ | 0% → Tests created ✅ |
| Authorization Engine | 85%+ | 0% → Need more tests |
| Role Hierarchy | 85%+ | 0% → Need more tests |
| Policy Evaluator | 90%+ | 0% → Need more tests |
| Main RBAC Class | 80%+ | 0% → Tests created ✅ |
| **Overall** | **80%+** | **0%** → **Target** |

## 🧪 Test Structure

```
tests/
├── __init__.py          # Test package
├── conftest.py          # PyTest fixtures
├── test_models.py       # Data model tests (✅ Created)
├── test_storage.py      # Storage layer tests (✅ Created)
├── test_rbac.py         # Main RBAC class tests (✅ Created)
├── test_engine.py       # Auth engine tests (TODO)
├── test_hierarchy.py    # Role hierarchy tests (TODO)
└── test_evaluator.py    # Policy evaluator tests (TODO)
```

## 📋 Configuration Files

All configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-v",
    "--cov=src/rbac",
    "--cov-report=html",
    "--cov-fail-under=80"
]

[tool.black]
line-length = 100
target-version = ['py313']

[tool.mypy]
python_version = "3.13"
warn_return_any = true
disallow_untyped_defs = true
```

## 🎯 Next Steps

1. **Run validation script**
   ```bash
   ./validate-code.bat  # or ./validate-code.sh
   ```

2. **Review generated reports**
   - `htmlcov/index.html` - Coverage report
   - `pylint-report.txt` - Code quality
   - `flake8-report.txt` - Style issues
   - `bandit-report.txt` - Security issues

3. **Set up SonarQube**
   - Install SonarQube (Docker recommended)
   - Generate authentication token
   - Run `sonar-scan.bat` or `sonar-scan.sh`

4. **Add more tests**
   - Create `test_engine.py`
   - Create `test_hierarchy.py`
   - Create `test_evaluator.py`
   - Target: 80%+ coverage

5. **Fix code quality issues**
   - Run formatters: `black src tests && isort src tests`
   - Fix Pylint warnings
   - Add type hints for MyPy

## 📚 Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [SonarQube Documentation](https://docs.sonarsource.com/sonarqube/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
