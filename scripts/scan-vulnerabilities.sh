#!/bin/bash
#
# Scan Python dependencies for known security vulnerabilities.
#
# This script runs multiple security scanners (safety, pip-audit) to detect
# vulnerabilities in project dependencies and generates a comprehensive report.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

JSON_OUTPUT=false
FAIL_ON_VULNERABILITIES=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --no-fail)
            FAIL_ON_VULNERABILITIES=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     RBAC Algorithm - Dependency Vulnerability Scanner         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

cd "$PROJECT_ROOT"

# Check if required tools are installed
echo "📦 Checking required tools..."

TOOLS_NEEDED=()

if ! command -v safety &> /dev/null; then
    TOOLS_NEEDED+=("safety")
fi

if ! command -v pip-audit &> /dev/null; then
    TOOLS_NEEDED+=("pip-audit")
fi

if [ ${#TOOLS_NEEDED[@]} -gt 0 ]; then
    echo "⚠️  Missing tools: ${TOOLS_NEEDED[*]}"
    echo "Installing required tools..."
    
    for tool in "${TOOLS_NEEDED[@]}"; do
        echo "  Installing $tool..."
        pip install "$tool"
    done
    echo ""
fi

# Create reports directory
REPORTS_DIR="$PROJECT_ROOT/reports"
mkdir -p "$REPORTS_DIR"

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
VULNERABILITIES_FOUND=false

# Run Safety check
echo "🔒 Running Safety vulnerability check..."
echo "   (Checking against Safety DB for known vulnerabilities)"
echo ""

if [ "$JSON_OUTPUT" = true ]; then
    SAFETY_OUTPUT="$REPORTS_DIR/safety-report_$TIMESTAMP.json"
    
    if ! safety check --json --output "$SAFETY_OUTPUT" 2>&1; then
        VULNERABILITIES_FOUND=true
        echo "❌ Safety found vulnerabilities! See: $SAFETY_OUTPUT"
        
        # Display summary
        VULN_COUNT=$(jq 'length' "$SAFETY_OUTPUT")
        echo "   Found $VULN_COUNT vulnerable packages"
    else
        echo "✅ Safety check passed - no known vulnerabilities"
    fi
else
    if ! safety check; then
        VULNERABILITIES_FOUND=true
        echo "❌ Safety found vulnerabilities!"
    else
        echo "✅ Safety check passed - no known vulnerabilities"
    fi
fi

echo ""

# Run pip-audit check
echo "🔍 Running pip-audit vulnerability check..."
echo "   (Checking against PyPI and OSV databases)"
echo ""

if [ "$JSON_OUTPUT" = true ]; then
    AUDIT_OUTPUT="$REPORTS_DIR/pip-audit-report_$TIMESTAMP.json"
    
    if ! pip-audit --format json --output "$AUDIT_OUTPUT" 2>&1; then
        VULNERABILITIES_FOUND=true
        echo "❌ pip-audit found vulnerabilities! See: $AUDIT_OUTPUT"
    else
        echo "✅ pip-audit check passed - no vulnerabilities found"
    fi
else
    if ! pip-audit --desc; then
        VULNERABILITIES_FOUND=true
        echo "❌ pip-audit found vulnerabilities!"
    else
        echo "✅ pip-audit check passed - no vulnerabilities found"
    fi
fi

echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════"
if [ "$VULNERABILITIES_FOUND" = true ]; then
    echo "⚠️  VULNERABILITY SCAN COMPLETE - ISSUES FOUND"
    echo ""
    echo "Recommendations:"
    echo "  1. Review the detailed reports above"
    echo "  2. Update vulnerable packages: pip install --upgrade <package>"
    echo "  3. Check for breaking changes before updating"
    echo "  4. Re-run tests after updates"
    
    if [ "$FAIL_ON_VULNERABILITIES" = true ]; then
        echo ""
        echo "Exiting with error code due to vulnerabilities..."
        exit 1
    fi
else
    echo "✅ VULNERABILITY SCAN COMPLETE - NO ISSUES FOUND"
    echo ""
    echo "All dependencies are secure! 🎉"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [ "$JSON_OUTPUT" = true ]; then
    echo "📄 Reports saved to: $REPORTS_DIR"
fi

exit 0
