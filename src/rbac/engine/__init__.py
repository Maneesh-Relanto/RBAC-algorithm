"""Authorization engine for RBAC system.

This module contains the core authorization logic that evaluates
permissions, resolves role hierarchies, and makes access control decisions.
"""

from .engine import AuthorizationEngine
from .hierarchy import RoleHierarchyResolver
from .evaluator import PolicyEvaluator

__all__ = ['AuthorizationEngine', 'RoleHierarchyResolver', 'PolicyEvaluator']
