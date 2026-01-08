@echo off
REM Quick script to start the interactive documentation

cd /d "%~dp0.."

echo.
echo ================================================================================
echo   RBAC Algorithm - Interactive Documentation
echo ================================================================================
echo.
echo Starting documentation server...
echo.

cd docs

if not exist "node_modules" (
    echo First time setup: Installing dependencies...
    echo This may take a few minutes...
    echo.
    call npm install
    echo.
    echo Installation complete!
    echo.
)

echo Starting server...
echo The documentation will open automatically in your browser.
echo.
echo Access at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server.
echo.

call npm start

pause
