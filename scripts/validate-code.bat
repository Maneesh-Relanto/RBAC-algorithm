@echo off
REM Code Quality Validation Script for Windows
REM This script runs all code quality checks

cd /d "%~dp0.."

echo.
echo ========================================
echo  RBAC Algorithm - Code Quality Check
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run:
    echo   python -m venv venv
    echo   .\venv\Scripts\activate
    echo   pip install -r .quality\requirements-dev.txt
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo [1/7] Running Black (Code Formatter Check)...
black --check src tests
if errorlevel 1 (
    echo [FAIL] Black found formatting issues. Run: black src tests
    set "BLACK_FAILED=1"
) else (
    echo [PASS] Black check passed
)

echo.
echo [2/7] Running isort (Import Sorting Check)...
isort --check-only src tests
if errorlevel 1 (
    echo [FAIL] isort found issues. Run: isort src tests
    set "ISORT_FAILED=1"
) else (
    echo [PASS] isort check passed
)

echo.
echo [3/7] Running Pylint (Code Analysis)...
pylint src --output-format=text --reports=y > pylint-report.txt
if errorlevel 1 (
    echo [WARN] Pylint found issues. Check pylint-report.txt
    set "PYLINT_WARN=1"
) else (
    echo [PASS] Pylint check passed
)

echo.
echo [4/7] Running Flake8 (Style Guide Enforcement)...
flake8 src tests --max-line-length=100 --count --statistics > flake8-report.txt
if errorlevel 1 (
    echo [WARN] Flake8 found issues. Check flake8-report.txt
    set "FLAKE8_WARN=1"
) else (
    echo [PASS] Flake8 check passed
)

echo.
echo [5/7] Running MyPy (Type Checking)...
mypy src
if errorlevel 1 (
    echo [WARN] MyPy found type issues
    set "MYPY_WARN=1"
) else (
    echo [PASS] MyPy check passed
)

echo.
echo [6/7] Running Bandit (Security Analysis)...
bandit -r src -f txt -o bandit-report.txt
if errorlevel 1 (
    echo [WARN] Bandit found security issues. Check bandit-report.txt
    set "BANDIT_WARN=1"
) else (
    echo [PASS] Bandit check passed
)

echo.
echo [7/7] Running PyTest (Unit Tests)...
pytest tests -v --cov=src/rbac --cov-report=html --cov-report=xml --cov-report=term-missing
if errorlevel 1 (
    echo [FAIL] Tests failed
    set "TESTS_FAILED=1"
) else (
    echo [PASS] All tests passed
)

echo.
echo ========================================
echo  Summary
echo ========================================
if defined BLACK_FAILED echo [!] Black formatting needed
if defined ISORT_FAILED echo [!] isort formatting needed
if defined PYLINT_WARN echo [!] Pylint warnings found
if defined FLAKE8_WARN echo [!] Flake8 warnings found
if defined MYPY_WARN echo [!] MyPy type issues found
if defined BANDIT_WARN echo [!] Security issues found
if defined TESTS_FAILED echo [!] Tests failed

if defined BLACK_FAILED goto fail
if defined ISORT_FAILED goto fail
if defined TESTS_FAILED goto fail

echo.
echo [SUCCESS] All mandatory checks passed!
echo Generated reports:
echo   - pylint-report.txt
echo   - flake8-report.txt
echo   - bandit-report.txt
echo   - htmlcov/index.html (coverage report)
echo   - coverage.xml (for SonarQube)
goto end

:fail
echo.
echo [FAILED] Some checks failed. Please fix the issues above.
exit /b 1

:end
