@echo off
REM SonarQube Analysis Script for Windows

cd /d "%~dp0..\.."

echo.
echo ========================================
echo  RBAC Algorithm - SonarQube Analysis
echo ========================================
echo.

REM Check if SonarQube scanner is installed
where sonar-scanner >nul 2>nul
if errorlevel 1 (
    echo [ERROR] SonarQube Scanner not found!
    echo.
    echo Please install SonarQube Scanner:
    echo 1. Download from: https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/scanners/sonarscanner/
    echo 2. Add to PATH or set SONAR_SCANNER_HOME
    echo.
    echo Alternatively, use Docker:
    echo   docker run --rm -v "%cd%:/usr/src" sonarsource/sonar-scanner-cli
    exit /b 1
)

REM Check if code quality reports exist
if not exist "coverage.xml" (
    echo [WARN] coverage.xml not found. Running tests first...
    call validate-code.bat
)

echo.
echo [INFO] Starting SonarQube analysis...
echo [INFO] Project: rbac-algorithm
echo.

REM Run SonarQube scanner
sonar-scanner ^
  -Dsonar.projectKey=rbac-algorithm ^
  -Dsonar.sources=src ^
  -Dsonar.tests=tests ^
  -Dsonar.python.version=3.13 ^
  -Dsonar.python.coverage.reportPaths=coverage.xml ^
  -Dsonar.python.pylint.reportPath=pylint-report.txt ^
  -Dsonar.python.flake8.reportPaths=flake8-report.txt ^
  -Dsonar.host.url=%SONAR_HOST_URL% ^
  -Dsonar.login=%SONAR_TOKEN%

if errorlevel 1 (
    echo.
    echo [FAIL] SonarQube analysis failed
    exit /b 1
)

echo.
echo [SUCCESS] SonarQube analysis completed!
echo View results at: %SONAR_HOST_URL%/dashboard?id=rbac-algorithm
