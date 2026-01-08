#!/bin/bash
# SonarQube Analysis Script for Linux/Mac

set -e

cd "$(dirname "$0")/../.."

echo ""
echo "========================================"
echo " RBAC Algorithm - SonarQube Analysis"
echo "========================================"
echo ""

# Check if SonarQube scanner is installed
if ! command -v sonar-scanner &> /dev/null; then
    echo "[ERROR] SonarQube Scanner not found!"
    echo ""
    echo "Please install SonarQube Scanner:"
    echo "1. Download from: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/scanners/sonarscanner/"
    echo "2. Add to PATH or set SONAR_SCANNER_HOME"
    echo ""
    echo "Alternatively, use Docker:"
    echo "  docker run --rm -v \"\$(pwd):/usr/src\" sonarsource/sonar-scanner-cli"
    exit 1
fi

# Check if code quality reports exist
if [ ! -f "coverage.xml" ]; then
    echo "[WARN] coverage.xml not found. Running tests first..."
    ./validate-code.sh
fi

echo ""
echo "[INFO] Starting SonarQube analysis..."
echo "[INFO] Project: rbac-algorithm"
echo ""

# Check for required environment variables
if [ -z "$SONAR_HOST_URL" ]; then
    echo "[WARN] SONAR_HOST_URL not set. Using default: http://localhost:9000"
    export SONAR_HOST_URL="http://localhost:9000"
fi

if [ -z "$SONAR_TOKEN" ]; then
    echo "[ERROR] SONAR_TOKEN not set. Please set your SonarQube token:"
    echo "  export SONAR_TOKEN=your-token-here"
    exit 1
fi

# Run SonarQube scanner
sonar-scanner \
  -Dsonar.projectKey=rbac-algorithm \
  -Dsonar.sources=src \
  -Dsonar.tests=tests \
  -Dsonar.python.version=3.13 \
  -Dsonar.python.coverage.reportPaths=coverage.xml \
  -Dsonar.python.pylint.reportPath=pylint-report.txt \
  -Dsonar.python.flake8.reportPaths=flake8-report.txt \
  -Dsonar.host.url="$SONAR_HOST_URL" \
  -Dsonar.login="$SONAR_TOKEN"

echo ""
echo "[SUCCESS] SonarQube analysis completed!"
echo "View results at: $SONAR_HOST_URL/dashboard?id=rbac-algorithm"
