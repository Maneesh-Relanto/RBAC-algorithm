#!/bin/bash
#
# Comprehensive validation suite for RBAC Algorithm (Priority 1 Checks).
#
# Runs all Priority 1 validation checks:
# - Property-based testing with Hypothesis
# - Integration tests
# - Branch coverage analysis (95%+ target)
# - Dependency vulnerability scanning

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

SKIP_VULN_SCAN=false
GENERATE_REPORTS=true
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-vuln-scan)
            SKIP_VULN_SCAN=true
            shift
            ;;
        --no-reports)
            GENERATE_REPORTS=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function write_header() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $(printf '%-60s' "$1")  ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

function write_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

function write_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function write_error() {
    echo -e "${RED}❌ $1${NC}"
}

function write_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

cd "$PROJECT_ROOT"

write_header "RBAC Algorithm - Priority 1 Validation Suite"

# Track results
declare -A results
START_TIME=$(date +%s)

# ========================================
# Step 1: Property-Based Tests
# ========================================
write_header "1. Property-Based Testing (Hypothesis)"
write_step "Running property-based tests to validate invariants..."

if [ "$VERBOSE" = true ]; then
    pytest tests/property/ -v -m property --tb=short
else
    pytest tests/property/ -m property --tb=short -q
fi

if [ $? -eq 0 ]; then
    write_success "Property-based tests passed!"
    results[PropertyTests]="PASS"
else
    write_error "Property-based tests failed!"
    results[PropertyTests]="FAIL"
fi

# ========================================
# Step 2: Integration Tests
# ========================================
write_header "2. Integration Testing"
write_step "Running integration tests for complete workflows..."

if [ "$VERBOSE" = true ]; then
    pytest tests/integration/ -v -m integration --tb=short
else
    pytest tests/integration/ -m integration --tb=short -q
fi

if [ $? -eq 0 ]; then
    write_success "Integration tests passed!"
    results[IntegrationTests]="PASS"
else
    write_error "Integration tests failed!"
    results[IntegrationTests]="FAIL"
fi

# ========================================
# Step 3: Branch Coverage Analysis
# ========================================
write_header "3. Branch Coverage Analysis (Target: 95%+)"
write_step "Running full test suite with branch coverage..."

pytest tests/ --cov=src --cov-branch --cov-report=term-missing --cov-report=html:reports/coverage --cov-fail-under=95

if [ $? -eq 0 ]; then
    write_success "Branch coverage target achieved (≥95%)!"
    results[BranchCoverage]="PASS"
    
    if [ "$GENERATE_REPORTS" = true ]; then
        write_info "Coverage report generated: reports/coverage/index.html"
    fi
else
    write_error "Branch coverage below target (<95%)!"
    results[BranchCoverage]="FAIL"
fi

# ========================================
# Step 4: Vulnerability Scanning
# ========================================
if [ "$SKIP_VULN_SCAN" = false ]; then
    write_header "4. Dependency Vulnerability Scanning"
    write_step "Scanning dependencies for known vulnerabilities..."
    
    SCAN_SCRIPT="$SCRIPT_DIR/scan-vulnerabilities.sh"
    
    if [ -f "$SCAN_SCRIPT" ]; then
        bash "$SCAN_SCRIPT" --no-fail
        
        if [ $? -eq 0 ]; then
            write_success "No vulnerabilities found!"
            results[VulnerabilityScan]="PASS"
        else
            write_error "Vulnerabilities detected!"
            results[VulnerabilityScan]="FAIL"
        fi
    else
        write_info "Vulnerability scan script not found, skipping..."
        results[VulnerabilityScan]="SKIP"
    fi
else
    write_info "Skipping vulnerability scan (--skip-vuln-scan specified)"
    results[VulnerabilityScan]="SKIP"
fi

# ========================================
# Summary Report
# ========================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

write_header "Validation Summary"

echo "┌────────────────────────────────────────────────────────────┐"
echo "│  Check                          │  Result                  │"
echo "├────────────────────────────────────────────────────────────┤"

function format_result() {
    local name="$1"
    local result="$2"
    
    local color=$NC
    case $result in
        PASS) color=$GREEN ;;
        FAIL) color=$RED ;;
        ERROR) color=$RED ;;
        SKIP) color=$YELLOW ;;
    esac
    
    printf "│  %-30s │  ${color}%-24s${NC}│\n" "$name" "$result"
}

format_result "Property-Based Tests" "${results[PropertyTests]}"
format_result "Integration Tests" "${results[IntegrationTests]}"
format_result "Branch Coverage (≥95%)" "${results[BranchCoverage]}"
format_result "Vulnerability Scan" "${results[VulnerabilityScan]}"

echo "└────────────────────────────────────────────────────────────┘"
echo ""

# Calculate pass rate
TOTAL_CHECKS=0
PASSED_CHECKS=0

for result in "${results[@]}"; do
    if [ "$result" != "SKIP" ]; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        if [ "$result" = "PASS" ]; then
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        fi
    fi
done

PASS_RATE=0
if [ $TOTAL_CHECKS -gt 0 ]; then
    PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
fi

echo -e "${CYAN}Duration: ${DURATION} seconds${NC}"
echo -e "${CYAN}Pass Rate: ${PASS_RATE}% ($PASSED_CHECKS/$TOTAL_CHECKS checks)${NC}"
echo ""

# Overall result
ALL_PASSED=true
for result in "${results[@]}"; do
    if [ "$result" = "FAIL" ] || [ "$result" = "ERROR" ]; then
        ALL_PASSED=false
        break
    fi
done

if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ ALL PRIORITY 1 VALIDATIONS PASSED! ✅              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    write_success "Your RBAC codebase meets all Priority 1 quality standards!"
    echo ""
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║          ⚠️  SOME VALIDATIONS FAILED  ⚠️                       ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    write_error "Please review the failures above and fix the issues."
    echo ""
    exit 1
fi
