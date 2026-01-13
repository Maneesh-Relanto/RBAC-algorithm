# Repository Health

This directory contains baseline quality metrics and instructions for maintaining code health.

## 📊 Baseline Metrics (Jan 13, 2026)

These baseline artifacts establish the initial quality standards for the RBAC Algorithm project:

- **Test Coverage**: 95%+ (verified)
- **Code Quality**: A-grade maintainability (SonarQube)
- **Performance**: 10,328 permission checks/second
- **Security**: Zero vulnerabilities
- **Bugs**: Zero detected
- **Dependencies**: Zero production dependencies

## 📁 Structure

```
repo-health/
├── baseline/                    # Initial quality snapshots (committed)
│   ├── coverage-baseline.txt   # Coverage report
│   ├── benchmark-baseline.txt  # Performance metrics
│   └── sonarqube-baseline.md   # Code quality summary
├── badges/                      # Badge configuration
│   └── shield-configs.md       # Badge definitions
└── README.md                    # This file
```

## 🔄 Generating Fresh Reports

### Run Tests with Coverage
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=term --cov-report=html

# View coverage: open htmlcov/index.html
```

### Run Performance Benchmarks
```bash
# Quick benchmark (30 seconds)
python benchmarks/quick_benchmark.py

# Full benchmark suite
python benchmarks/performance_benchmark.py
```

### Run SonarQube Analysis
```bash
# Use SonarQube extension in VS Code
# Or run: sonar-scanner (requires SonarQube setup)
```

## 📌 Quality Standards

All contributions must maintain or exceed these baseline metrics:

| Metric | Threshold | Current |
|--------|-----------|---------|
| Test Coverage | ≥95% | 95%+ ✅ |
| Code Quality | ≥A grade | A ✅ |
| Performance | ≥10K checks/sec | 10,328 ✅ |
| Security Issues | 0 | 0 ✅ |
| Bugs | 0 | 0 ✅ |

## 🎯 CI/CD Integration (Future)

Planned automation:
- GitHub Actions for test runs
- Codecov for coverage tracking
- SonarCloud for continuous quality analysis
- Automated benchmark comparisons

## 📝 Notes

- Baseline reports are committed to establish reference points
- Fresh reports (generated locally) are ignored by Git
- Update baselines only when making intentional quality improvements
