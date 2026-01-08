#!/bin/bash
# Code Quality Validation Script for Linux/Mac
# This script runs all code quality checks

set -e

cd "$(dirname "$0")/.."

echo ""
echo "========================================"
echo " RBAC Algorithm - Code Quality Check"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] Virtual environment not found. Please run:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements-dev.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

FAILED=0

echo "[1/7] Running Black (Code Formatter Check)..."
if black --check src tests; then
    echo "[PASS] Black check passed"
else
    echo "[FAIL] Black found formatting issues. Run: black src tests"
    FAILED=1
fi

echo ""
echo "[2/7] Running isort (Import Sorting Check)..."
if isort --check-only src tests; then
    echo "[PASS] isort check passed"
else
    echo "[FAIL] isort found issues. Run: isort src tests"
    FAILED=1
fi

echo ""
echo "[3/7] Running Pylint (Code Analysis)..."
if pylint src --output-format=text --reports=y > pylint-report.txt; then
    echo "[PASS] Pylint check passed"
else
    echo "[WARN] Pylint found issues. Check pylint-report.txt"
fi

echo ""
echo "[4/7] Running Flake8 (Style Guide Enforcement)..."
if flake8 src tests --max-line-length=100 --count --statistics > flake8-report.txt; then
    echo "[PASS] Flake8 check passed"
else
    echo "[WARN] Flake8 found issues. Check flake8-report.txt"
fi

echo ""
echo "[5/7] Running MyPy (Type Checking)..."
if mypy src; then
    echo "[PASS] MyPy check passed"
else
    echo "[WARN] MyPy found type issues"
fi

echo ""
echo "[6/7] Running Bandit (Security Analysis)..."
if bandit -r src -f txt -o bandit-report.txt; then
    echo "[PASS] Bandit check passed"
else
    echo "[WARN] Bandit found security issues. Check bandit-report.txt"
fi

echo ""
echo "[7/7] Running PyTest (Unit Tests)..."
if pytest tests -v --cov=src/rbac --cov-report=html --cov-report=xml --cov-report=term-missing; then
    echo "[PASS] All tests passed"
else
    echo "[FAIL] Tests failed"
    FAILED=1
fi

echo ""
echo "========================================"
echo " Summary"
echo "========================================"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "[SUCCESS] All mandatory checks passed!"
    echo "Generated reports:"
    echo "  - pylint-report.txt"
    echo "  - flake8-report.txt"
    echo "  - bandit-report.txt"
    echo "  - htmlcov/index.html (coverage report)"
    echo "  - coverage.xml (for SonarQube)"
else
    echo ""
    echo "[FAILED] Some checks failed. Please fix the issues above."
    exit 1
fi
