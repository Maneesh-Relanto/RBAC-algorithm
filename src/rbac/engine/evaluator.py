"""Policy evaluator for attribute-based access control (ABAC).

Evaluates conditions on permissions to enable context-aware authorization.
Supports operators like ==, !=, >, <, in, contains, etc.
"""

from typing import Any, Dict, Optional, List
import re
from datetime import datetime, time
import operator

from ..core.protocols import IPolicyEvaluator
from ..core.exceptions import PolicyEvaluationError


class PolicyEvaluator(IPolicyEvaluator):
    """Evaluates ABAC policy conditions.
    
    Conditions are expressed as dictionaries with operators:
    
    Examples:
        # Simple equality
        {"user.department": {"==": "engineering"}}
        
        # Comparison
        {"resource.owner_id": {"==": "{{user.id}}"}}
        
        # Multiple conditions (AND)
        {
            "user.level": {">": 5},
            "resource.status": {"==": "published"}
        }
        
        # List membership
        {"user.roles": {"contains": "admin"}}
        
        # Time-based
        {"context.time": {">": "09:00", "<": "17:00"}}
    """
    
    # Supported operators
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        'in': lambda a, b: a in b,
        'not_in': lambda a, b: a not in b,
        'contains': lambda a, b: b in a,
        'not_contains': lambda a, b: b not in a,
        'startswith': lambda a, b: str(a).startswith(str(b)),
        'endswith': lambda a, b: str(a).endswith(str(b)),
        'matches': lambda a, b: bool(re.match(str(b), str(a))),
    }
    
    def __init__(self):
        """Initialize the policy evaluator."""
        pass
    
    def evaluate(
        self,
        conditions: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate if conditions are satisfied given a context.
        
        Args:
            conditions: Policy conditions to evaluate
            context: Context data (user attributes, resource attributes, etc.)
            
        Returns:
            True if all conditions are satisfied, False otherwise
            
        Raises:
            PolicyEvaluationError: If condition format is invalid
        """
        # No conditions = always allow
        if not conditions:
            return True
        
        if not isinstance(conditions, dict):
            raise PolicyEvaluationError(
                "Conditions must be a dictionary"
            )
        
        # Evaluate all conditions (AND logic)
        for field_path, operators_dict in conditions.items():
            if not self._evaluate_field(field_path, operators_dict, context):
                return False
        
        return True
    
    def evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        user: Any,
        resource: Any,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate ABAC conditions (protocol method).
        
        Args:
            conditions: Conditions to evaluate
            user: User object
            resource: Resource object
            context: Additional context
            
        Returns:
            True if all conditions pass
        """
        # Build full context from user and resource
        full_context = dict(context) if context else {}
        
        # Add user attributes
        if user:
            full_context['user'] = {
                'id': getattr(user, 'id', None),
                'email': getattr(user, 'email', None),
                'name': getattr(user, 'name', None),
                **getattr(user, 'attributes', {})
            }
        
        # Add resource attributes
        if resource:
            full_context['resource'] = {
                'id': getattr(resource, 'id', None),
                'type': getattr(resource, 'type', None),
                **getattr(resource, 'attributes', {})
            }
        
        return self.evaluate(conditions, full_context)
    
    def evaluate_batch(
        self,
        conditions: Optional[Dict[str, Any]],
        contexts: List[Dict[str, Any]]
    ) -> List[bool]:
        """Evaluate conditions against multiple contexts.
        
        Args:
            conditions: Policy conditions to evaluate
            contexts: List of context dictionaries
            
        Returns:
            List of boolean results, one per context
        """
        return [self.evaluate(conditions, ctx) for ctx in contexts]
    
    def _evaluate_field(
        self,
        field_path: str,
        operators_dict: Any,
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate conditions for a single field.
        
        Args:
            field_path: Dot-notation path like "user.department"
            operators_dict: Dictionary of operator -> value
            context: Context data
            
        Returns:
            True if all operators for this field are satisfied
        """
        if not isinstance(operators_dict, dict):
            raise PolicyEvaluationError(
                f"Operators for '{field_path}' must be a dictionary"
            )
        
        # Get the actual value from context
        try:
            actual_value = self._get_nested_value(field_path, context)
        except KeyError:
            # Field not in context = condition fails
            return False
        
        # Evaluate each operator
        for op, expected_value in operators_dict.items():
            # Resolve template variables in expected value
            expected_value = self._resolve_template(expected_value, context)
            
            if not self._apply_operator(op, actual_value, expected_value):
                return False
        
        return True
    
    def _get_nested_value(
        self,
        path: str,
        data: Dict[str, Any]
    ) -> Any:
        """Get a value from nested dictionary using dot notation.
        
        Examples:
            _get_nested_value("user.id", {"user": {"id": "123"}}) -> "123"
            _get_nested_value("tags[0]", {"tags": ["a", "b"]}) -> "a"
        """
        keys = path.split('.')
        value = data
        
        for key in keys:
            # Handle array indexing like "tags[0]"
            if '[' in key and ']' in key:
                key_name = key[:key.index('[')]
                index = int(key[key.index('[') + 1:key.index(']')])
                value = value[key_name][index]
            else:
                value = value[key]
        
        return value
    
    def _resolve_template(
        self,
        value: Any,
        context: Dict[str, Any]
    ) -> Any:
        """Resolve template variables like {{user.id}}.
        
        Examples:
            _resolve_template("{{user.id}}", {"user": {"id": "123"}}) -> "123"
            _resolve_template("fixed_value", {}) -> "fixed_value"
        """
        if not isinstance(value, str):
            return value
        
        # Check for template pattern {{...}}
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, value)
        
        if not matches:
            return value
        
        # Replace all template variables
        result = value
        for match in matches:
            try:
                resolved = self._get_nested_value(match.strip(), context)
                result = result.replace(f'{{{{{match}}}}}', str(resolved))
            except (KeyError, TypeError, IndexError):
                # Template variable not found = leave as is
                pass
        
        return result
    
    def _apply_operator(
        self,
        op: str,
        actual: Any,
        expected: Any
    ) -> bool:
        """Apply an operator to compare actual vs expected values.
        
        Args:
            op: Operator string like "==", ">", "contains"
            actual: Actual value from context
            expected: Expected value from condition
            
        Returns:
            True if condition is satisfied
            
        Raises:
            PolicyEvaluationError: If operator is unknown or comparison fails
        """
        if op not in self.OPERATORS:
            raise PolicyEvaluationError(f"Unknown operator: {op}")
        
        op_func = self.OPERATORS[op]
        
        try:
            # Type coercion for comparisons
            actual_converted, expected_converted = self._coerce_types(
                actual, expected
            )
            
            return op_func(actual_converted, expected_converted)
        except (TypeError, ValueError) as e:
            raise PolicyEvaluationError(
                f"Cannot compare {actual} with {expected} using {op}: {e}"
            )
    
    def _coerce_types(
        self,
        actual: Any,
        expected: Any
    ) -> tuple:
        """Coerce types to make them comparable.
        
        Handles cases like:
        - Comparing strings to numbers
        - Comparing strings to booleans
        - Time comparisons
        """
        # Both same type = no conversion needed
        if type(actual) == type(expected):
            return actual, expected
        
        # Try to convert expected to match actual's type
        actual_type = type(actual)
        
        # Number conversions
        if actual_type in (int, float):
            try:
                if isinstance(expected, str):
                    return actual, float(expected)
            except ValueError:
                pass
        
        # Boolean conversions
        if actual_type == bool and isinstance(expected, str):
            return actual, expected.lower() in ('true', '1', 'yes')
        
        # Time conversions (for time-based policies)
        if isinstance(actual, (datetime, time)) and isinstance(expected, str):
            try:
                expected_time = datetime.strptime(expected, '%H:%M').time()
                if isinstance(actual, datetime):
                    actual = actual.time()
                return actual, expected_time
            except ValueError:
                pass
        
        # List/set membership
        if isinstance(expected, (list, tuple, set)):
            return actual, expected
        
        # Default: convert both to strings for comparison
        return str(actual), str(expected)
    
    def _validate_field_path(self, field_path: str) -> None:
        """Validate a field path is a string."""
        if not isinstance(field_path, str):
            raise PolicyEvaluationError("Field paths must be strings")
    
    def _validate_operators_dict(self, field_path: str, operators_dict) -> None:
        """Validate operators dictionary for a field path."""
        if not isinstance(operators_dict, dict):
            raise PolicyEvaluationError(
                f"Operators for '{field_path}' must be a dictionary"
            )
        
        for op in operators_dict.keys():
            if op not in self.OPERATORS:
                raise PolicyEvaluationError(
                    f"Unknown operator: {op}. "
                    f"Supported: {', '.join(self.OPERATORS.keys())}"
                )
    
    def validate_conditions(self, conditions: Dict[str, Any]) -> bool:
        """Validate that conditions are well-formed.
        
        Args:
            conditions: Policy conditions to validate
            
        Returns:
            True if valid
            
        Raises:
            PolicyEvaluationError: If conditions are malformed
        """
        if not conditions:
            return True
        
        if not isinstance(conditions, dict):
            raise PolicyEvaluationError("Conditions must be a dictionary")
        
        for field_path, operators_dict in conditions.items():
            self._validate_field_path(field_path)
            self._validate_operators_dict(field_path, operators_dict)
        
        return True
