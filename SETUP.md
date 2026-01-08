# RBAC Algorithm - Complete Setup Guide

This guide will walk you through setting up the RBAC Algorithm library from scratch, including development environment, running examples, and deploying the documentation site.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Python Implementation Setup](#python-implementation-setup)
3. [Documentation Site Setup](#documentation-site-setup)
4. [Running Examples](#running-examples)
5. [Development Setup](#development-setup)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Python**: 3.8 or higher (tested on Python 3.13.7)
- **Node.js**: 16 or higher (for documentation site)
- **Git**: For cloning the repository
- **Code Editor**: VS Code recommended

### Check Installed Versions

```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check npm version
npm --version

# Check Git version
git --version
```

## Python Implementation Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/rbac-algorithm.git
cd rbac-algorithm
```

### Step 2: Create Virtual Environment

Creating a virtual environment isolates the project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt after activation.

### Step 3: Install Dependencies

```bash
# Install in development mode (recommended for development)
pip install -e .

# Or install dependencies manually
pip install dataclasses-json typing-extensions
```

### Step 4: Verify Installation

```python
# Create a test file: test_install.py
from rbac import RBAC

rbac = RBAC()
print("✅ RBAC Algorithm installed successfully!")
print(f"📦 Storage Backend: {type(rbac.storage).__name__}")
print(f"🔧 Engine: {type(rbac.engine).__name__}")
```

Run the test:

```bash
python test_install.py
```

## Documentation Site Setup

The documentation site is built with Docusaurus and React.

### Step 1: Navigate to Documentation Directory

```bash
cd docs
```

### Step 2: Install Node Dependencies

```bash
# This will install ~1,300 packages (~150 MB)
npm install
```

### Step 3: Start Development Server

```bash
# Start on port 3001
npm start -- --port 3001

# Or use default port 3000
npm start
```

The site will automatically open in your browser at `http://localhost:3001`.

### Step 4: Build for Production

```bash
# Build static files
npm run build

# The output will be in the 'build' directory
```

### Step 5: Deploy (Optional)

```bash
# Deploy to GitHub Pages
npm run deploy

# Or deploy to custom hosting
# Copy the 'build' folder to your web server
```

## Running Examples

The repository includes two complete examples demonstrating the RBAC system.

### Basic Usage Example

```bash
# From the project root directory
python examples/basic_usage.py
```

**What it demonstrates:**
- Creating users, roles, and permissions
- Role hierarchy (Manager → Developer → Viewer)
- Permission inheritance
- Basic authorization checks

### ABAC Example

```bash
python examples/abac_example.py
```

**What it demonstrates:**
- Attribute-Based Access Control
- Dynamic conditions on permissions
- Context-aware authorization
- Advanced use cases (time-based, ownership checks)

## Development Setup

### Directory Structure

```
rbac-algorithm/
├── src/
│   └── rbac/
│       ├── __init__.py           # Main RBAC class
│       ├── core/                 # Core models
│       ├── storage/              # Storage backends
│       └── engine/               # Authorization engine
├── examples/                     # Usage examples
├── docs/                         # Documentation site
│   ├── docs/                     # Markdown docs
│   ├── src/                      # React components
│   └── static/                   # Static assets
├── tests/                        # Unit tests (to be added)
├── README.md                     # Main readme
└── setup.py                      # Python package setup
```

### Setting Up Git

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: RBAC Algorithm implementation"

# Add remote repository
git remote add origin https://github.com/yourusername/rbac-algorithm.git

# Push to remote
git push -u origin main
```

### Running Tests

```bash
# Install pytest
pip install pytest pytest-cov

# Run tests (when test suite is created)
pytest

# Run with coverage
pytest --cov=rbac tests/
```

### Code Style

```bash
# Install formatting tools
pip install black flake8 mypy

# Format code
black src/

# Check code style
flake8 src/

# Type checking
mypy src/
```

## Troubleshooting

### Python Issues

#### Issue: "Module not found" error

```bash
# Solution: Install in development mode
pip install -e .

# Or add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%cd%\src           # Windows
```

#### Issue: "Python version too old"

```bash
# Check version
python --version

# Install Python 3.8+ from python.org
# Or use pyenv to manage multiple versions
```

### Node.js Issues

#### Issue: "npm install fails"

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### Issue: "Port 3001 already in use"

```bash
# Use a different port
npm start -- --port 3002

# Or kill the process using port 3001
# Windows:
netstat -ano | findstr :3001
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3001 | xargs kill
```

### Documentation Site Issues

#### Issue: "Page not found" after navigation

```bash
# Clear Docusaurus cache
npm run clear

# Restart server
npm start
```

#### Issue: "Build fails"

```bash
# Check for syntax errors in markdown files
# Ensure all links are valid
# Check console for specific error messages
```

## Next Steps

After completing the setup:

1. **Explore the Code**: Start with `src/rbac/__init__.py`
2. **Run Examples**: Understand how to use the library
3. **Read Documentation**: Visit http://localhost:3001
4. **Try Interactive Playground**: Visit http://localhost:3001/playground
5. **Contribute**: Check CONTRIBUTING.md for guidelines

## Additional Resources

- **GitHub Repository**: https://github.com/yourusername/rbac-algorithm
- **Documentation Site**: https://your-domain.com
- **Issue Tracker**: https://github.com/yourusername/rbac-algorithm/issues
- **Discord Community**: https://discord.gg/your-invite

## Support

If you encounter issues not covered in this guide:

1. Check the [FAQ](docs/docs/faq.md)
2. Search [existing issues](https://github.com/yourusername/rbac-algorithm/issues)
3. Create a [new issue](https://github.com/yourusername/rbac-algorithm/issues/new)
4. Join our Discord community

---

**Last Updated**: January 2026  
**Maintainers**: RBAC Algorithm Team
