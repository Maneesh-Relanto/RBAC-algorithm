"""Setup configuration for RBAC Algorithm Python implementation."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version
version_file = Path(__file__).parent / "src" / "rbac" / "__init__.py"
version = "0.1.0"
if version_file.exists():
    for line in version_file.read_text().splitlines():
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

setup(
    name="rbac-algorithm",
    version=version,
    author="RBAC Algorithm Contributors",
    author_email="contact@rbac-algorithm.dev",
    description="Enterprise-grade Role-Based Access Control (RBAC) implementation with ABAC support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rbac-algorithm/rbac-python",
    project_urls={
        "Bug Tracker": "https://github.com/rbac-algorithm/rbac-python/issues",
        "Documentation": "https://rbac-algorithm.dev/docs",
        "Source Code": "https://github.com/rbac-algorithm/rbac-python",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pylint>=2.17.0",
        ],
        "sql": [
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",  # PostgreSQL
            "pymysql>=1.0.0",  # MySQL
        ],
        "redis": [
            "redis>=4.5.0",
        ],
        "async": [
            "aioredis>=2.0.0",
        ],
        "all": [
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.0.0",
            "redis>=4.5.0",
            "aioredis>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rbac=rbac.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "rbac",
        "access control",
        "authorization",
        "permissions",
        "roles",
        "abac",
        "security",
        "auth",
        "iam",
    ],
)
