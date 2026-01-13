#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Comprehensive validation suite for RBAC Algorithm (Priority 1 Checks).

.DESCRIPTION
    Runs all Priority 1 validation checks:
    - Property-based testing with Hypothesis
    - Integration tests
    - Branch coverage analysis (95%+ target)
    - Dependency vulnerability scanning

.EXAMPLE
    .\validate-priority1.ps1
    
.EXAMPLE
    .\validate-priority1.ps1 -SkipVulnerabilityScan
#>

param(
    [switch]$SkipVulnerabilityScan = $false,
    [switch]$GenerateReports = $true,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Continue"
$script_dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$project_root = Split-Path -Parent $script_dir

# Colors for output
function Write-Header($text) {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $($text.PadRight(60))  ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step($text) {
    Write-Host "▶ $text" -ForegroundColor Yellow
}

function Write-Success($text) {
    Write-Host "✅ $text" -ForegroundColor Green
}

function Write-Error-Custom($text) {
    Write-Host "❌ $text" -ForegroundColor Red
}

function Write-Info($text) {
    Write-Host "ℹ️  $text" -ForegroundColor Cyan
}

# Change to project root
Set-Location $project_root

Write-Header "RBAC Algorithm - Priority 1 Validation Suite"

# Track results
$results = @{
    PropertyTests = $null
    IntegrationTests = $null
    BranchCoverage = $null
    VulnerabilityScan = $null
}

$start_time = Get-Date

# ========================================
# Step 1: Property-Based Tests
# ========================================
Write-Header "1. Property-Based Testing (Hypothesis)"
Write-Step "Running property-based tests to validate invariants..."

try {
    if ($Verbose) {
        pytest tests/property/ -v -m property --tb=short
    } else {
        pytest tests/property/ -m property --tb=short -q
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Property-based tests passed!"
        $results.PropertyTests = "PASS"
    } else {
        Write-Error-Custom "Property-based tests failed!"
        $results.PropertyTests = "FAIL"
    }
} catch {
    Write-Error-Custom "Error running property-based tests: $_"
    $results.PropertyTests = "ERROR"
}

# ========================================
# Step 2: Integration Tests
# ========================================
Write-Header "2. Integration Testing"
Write-Step "Running integration tests for complete workflows..."

try {
    if ($Verbose) {
        pytest tests/integration/ -v -m integration --tb=short
    } else {
        pytest tests/integration/ -m integration --tb=short -q
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Integration tests passed!"
        $results.IntegrationTests = "PASS"
    } else {
        Write-Error-Custom "Integration tests failed!"
        $results.IntegrationTests = "FAIL"
    }
} catch {
    Write-Error-Custom "Error running integration tests: $_"
    $results.IntegrationTests = "ERROR"
}

# ========================================
# Step 3: Branch Coverage Analysis
# ========================================
Write-Header "3. Branch Coverage Analysis (Target: 95%+)"
Write-Step "Running full test suite with branch coverage..."

try {
    # Run all tests with coverage
    pytest tests/ --cov=src --cov-branch --cov-report=term-missing --cov-report=html:reports/coverage --cov-fail-under=95
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Branch coverage target achieved (≥95%)!"
        $results.BranchCoverage = "PASS"
        
        if ($GenerateReports) {
            Write-Info "Coverage report generated: reports/coverage/index.html"
        }
    } else {
        Write-Error-Custom "Branch coverage below target (<95%)!"
        $results.BranchCoverage = "FAIL"
    }
} catch {
    Write-Error-Custom "Error running coverage analysis: $_"
    $results.BranchCoverage = "ERROR"
}

# ========================================
# Step 4: Vulnerability Scanning
# ========================================
if (-not $SkipVulnerabilityScan) {
    Write-Header "4. Dependency Vulnerability Scanning"
    Write-Step "Scanning dependencies for known vulnerabilities..."
    
    try {
        $scan_script = Join-Path $script_dir "scan-vulnerabilities.ps1"
        
        if (Test-Path $scan_script) {
            & $scan_script -FailOnVulnerabilities:$false
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "No vulnerabilities found!"
                $results.VulnerabilityScan = "PASS"
            } else {
                Write-Error-Custom "Vulnerabilities detected!"
                $results.VulnerabilityScan = "FAIL"
            }
        } else {
            Write-Info "Vulnerability scan script not found, skipping..."
            $results.VulnerabilityScan = "SKIP"
        }
    } catch {
        Write-Error-Custom "Error running vulnerability scan: $_"
        $results.VulnerabilityScan = "ERROR"
    }
} else {
    Write-Info "Skipping vulnerability scan (--SkipVulnerabilityScan specified)"
    $results.VulnerabilityScan = "SKIP"
}

# ========================================
# Summary Report
# ========================================
$end_time = Get-Date
$duration = $end_time - $start_time

Write-Header "Validation Summary"

Write-Host "┌────────────────────────────────────────────────────────────┐" -ForegroundColor White
Write-Host "│  Check                          │  Result                  │" -ForegroundColor White
Write-Host "├────────────────────────────────────────────────────────────┤" -ForegroundColor White

function Format-Result($name, $result) {
    $name_padded = $name.PadRight(30)
    $result_padded = $result.PadRight(24)
    
    $color = switch ($result) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "ERROR" { "Red" }
        "SKIP" { "Yellow" }
        default { "Gray" }
    }
    
    Write-Host "│  $name_padded │  " -NoNewline -ForegroundColor White
    Write-Host $result_padded -NoNewline -ForegroundColor $color
    Write-Host "│" -ForegroundColor White
}

Format-Result "Property-Based Tests" $results.PropertyTests
Format-Result "Integration Tests" $results.IntegrationTests
Format-Result "Branch Coverage (≥95%)" $results.BranchCoverage
Format-Result "Vulnerability Scan" $results.VulnerabilityScan

Write-Host "└────────────────────────────────────────────────────────────┘" -ForegroundColor White
Write-Host ""

# Calculate pass rate
$total_checks = $results.Values | Where-Object { $_ -ne "SKIP" } | Measure-Object | Select-Object -ExpandProperty Count
$passed_checks = $results.Values | Where-Object { $_ -eq "PASS" } | Measure-Object | Select-Object -ExpandProperty Count
$pass_rate = if ($total_checks -gt 0) { ($passed_checks / $total_checks) * 100 } else { 0 }

Write-Host "Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Cyan
Write-Host "Pass Rate: $($pass_rate.ToString('F1'))% ($passed_checks/$total_checks checks)" -ForegroundColor $(if ($pass_rate -eq 100) { "Green" } else { "Yellow" })
Write-Host ""

# Overall result
$all_passed = ($results.Values | Where-Object { $_ -eq "FAIL" -or $_ -eq "ERROR" } | Measure-Object).Count -eq 0

if ($all_passed) {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║          ✅ ALL PRIORITY 1 VALIDATIONS PASSED! ✅              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Success "Your RBAC codebase meets all Priority 1 quality standards!"
    Write-Host ""
    exit 0
} else {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║          ⚠️  SOME VALIDATIONS FAILED  ⚠️                       ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
    Write-Host ""
    Write-Error-Custom "Please review the failures above and fix the issues."
    Write-Host ""
    exit 1
}
