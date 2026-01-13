#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Scan Python dependencies for known security vulnerabilities.

.DESCRIPTION
    This script runs multiple security scanners (safety, pip-audit) to detect
    vulnerabilities in project dependencies and generates a comprehensive report.

.EXAMPLE
    .\scan-vulnerabilities.ps1
#>

param(
    [switch]$JsonOutput = $false,
    [switch]$FailOnVulnerabilities = $true
)

$ErrorActionPreference = "Continue"
$script_dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$project_root = Split-Path -Parent $script_dir

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     RBAC Algorithm - Dependency Vulnerability Scanner         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Change to project root
Set-Location $project_root

# Check if required tools are installed
Write-Host "📦 Checking required tools..." -ForegroundColor Yellow

$tools_needed = @()

if (-not (Get-Command safety -ErrorAction SilentlyContinue)) {
    $tools_needed += "safety"
}

if (-not (Get-Command pip-audit -ErrorAction SilentlyContinue)) {
    $tools_needed += "pip-audit"
}

if ($tools_needed.Count -gt 0) {
    Write-Host "⚠️  Missing tools: $($tools_needed -join ', ')" -ForegroundColor Red
    Write-Host "Installing required tools..." -ForegroundColor Yellow
    
    foreach ($tool in $tools_needed) {
        Write-Host "  Installing $tool..." -ForegroundColor Gray
        pip install $tool
    }
    Write-Host ""
}

# Create reports directory
$reports_dir = Join-Path $project_root "reports"
if (-not (Test-Path $reports_dir)) {
    New-Item -ItemType Directory -Path $reports_dir | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$vulnerabilities_found = $false

# Run Safety check
Write-Host "🔒 Running Safety vulnerability check..." -ForegroundColor Yellow
Write-Host "   (Checking against Safety DB for known vulnerabilities)" -ForegroundColor Gray
Write-Host ""

if ($JsonOutput) {
    $safety_output = Join-Path $reports_dir "safety-report_$timestamp.json"
    safety check --json --output $safety_output 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        $vulnerabilities_found = $true
        Write-Host "❌ Safety found vulnerabilities! See: $safety_output" -ForegroundColor Red
        
        # Display summary
        $safety_data = Get-Content $safety_output | ConvertFrom-Json
        Write-Host "   Found $($safety_data.Count) vulnerable packages" -ForegroundColor Red
    } else {
        Write-Host "✅ Safety check passed - no known vulnerabilities" -ForegroundColor Green
    }
} else {
    safety check
    
    if ($LASTEXITCODE -ne 0) {
        $vulnerabilities_found = $true
        Write-Host "❌ Safety found vulnerabilities!" -ForegroundColor Red
    } else {
        Write-Host "✅ Safety check passed - no known vulnerabilities" -ForegroundColor Green
    }
}

Write-Host ""

# Run pip-audit check
Write-Host "🔍 Running pip-audit vulnerability check..." -ForegroundColor Yellow
Write-Host "   (Checking against PyPI and OSV databases)" -ForegroundColor Gray
Write-Host ""

if ($JsonOutput) {
    $audit_output = Join-Path $reports_dir "pip-audit-report_$timestamp.json"
    pip-audit --format json --output $audit_output 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        $vulnerabilities_found = $true
        Write-Host "❌ pip-audit found vulnerabilities! See: $audit_output" -ForegroundColor Red
        
        # Display summary
        $audit_data = Get-Content $audit_output | ConvertFrom-Json
        $vuln_count = ($audit_data.dependencies | Where-Object { $_.vulns.Count -gt 0 }).Count
        Write-Host "   Found vulnerabilities in $vuln_count packages" -ForegroundColor Red
    } else {
        Write-Host "✅ pip-audit check passed - no vulnerabilities found" -ForegroundColor Green
    }
} else {
    pip-audit --desc
    
    if ($LASTEXITCODE -ne 0) {
        $vulnerabilities_found = $true
        Write-Host "❌ pip-audit found vulnerabilities!" -ForegroundColor Red
    } else {
        Write-Host "✅ pip-audit check passed - no vulnerabilities found" -ForegroundColor Green
    }
}

Write-Host ""

# Summary
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
if ($vulnerabilities_found) {
    Write-Host "⚠️  VULNERABILITY SCAN COMPLETE - ISSUES FOUND" -ForegroundColor Red
    Write-Host ""
    Write-Host "Recommendations:" -ForegroundColor Yellow
    Write-Host "  1. Review the detailed reports above" -ForegroundColor Gray
    Write-Host "  2. Update vulnerable packages: pip install --upgrade <package>" -ForegroundColor Gray
    Write-Host "  3. Check for breaking changes before updating" -ForegroundColor Gray
    Write-Host "  4. Re-run tests after updates" -ForegroundColor Gray
    
    if ($FailOnVulnerabilities) {
        Write-Host ""
        Write-Host "Exiting with error code due to vulnerabilities..." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ VULNERABILITY SCAN COMPLETE - NO ISSUES FOUND" -ForegroundColor Green
    Write-Host ""
    Write-Host "All dependencies are secure! 🎉" -ForegroundColor Green
}
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($JsonOutput) {
    Write-Host "📄 Reports saved to: $reports_dir" -ForegroundColor Cyan
}

exit 0
