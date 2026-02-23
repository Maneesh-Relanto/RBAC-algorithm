"""
RBAC Decorators for Flask Blog API.
Provides decorators for permission and role-based authorization.
"""
import logging
from functools import wraps
from flask import g, jsonify
from auth import get_current_user

logger = logging.getLogger(__name__)

# Error/message constants to avoid duplication
MSG_AUTH_REQUIRED = 'Authentication required'
MSG_LOGIN_REQUIRED = 'You must be logged in to perform this action'


# ---------------------------------------------------------------------------
# Private helpers (reduce cognitive complexity in the decorators below)
# ---------------------------------------------------------------------------

# Roles that can perform ownership-protected actions on ANY resource
OWNERSHIP_OVERRIDE_ROLES = frozenset({'admin', 'editor'})


def _fetch_owned_resource(storage, resource_type, kwargs):
    """Return the owned resource for an ownership check, or (None, error) if not found."""
    resource_id = kwargs.get('post_id') or kwargs.get('comment_id') or kwargs.get('id')
    if not resource_id:
        return None, None

    resource_id = str(resource_id)  # Flask URL converters may yield int
    if 'post' in (resource_type or ''):
        resource = storage.get_post(resource_id)
    elif 'comment' in (resource_type or ''):
        resource = storage.get_comment(resource_id)
    else:
        resource = None

    if not resource:
        error = (
            jsonify({'error': 'Not found', 'message': f'{resource_type.capitalize()} not found'}),
            404,
        )
        return None, error
    return resource, None


def _build_permission_context(user, resource):
    """Build the ABAC context dict used during the RBAC check."""
    context = {
        'user_id': user['user_id'],
        'username': user['username'],
        'role': user['role'],
    }
    if resource:
        owner_id = getattr(resource, 'author_id', None) or getattr(resource, 'user_id', None)
        context['resource_owner'] = owner_id
        context['is_owner'] = owner_id == user['user_id']
    return context


def _forbidden_response(check_ownership, resource, context, action, resource_type):
    """Return a 403 response tuple for a failed permission check."""
    if check_ownership and resource and not context.get('is_owner'):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You can only modify your own content',
            'reason': 'ownership_required',
        }), 403
    return jsonify({
        'error': 'Forbidden',
        'message': f'You do not have permission to {action} {resource_type}',
        'reason': 'permission_denied',
    }), 403


def require_permission(action: str, resource_type: str = None, check_ownership: bool = False):
    """
    Decorator to require specific permission for a route.

    Args:
        action: The action to check (e.g., 'create', 'read', 'update', 'delete')
        resource_type: The resource type (e.g., 'post', 'comment'). If None, uses action only
        check_ownership: If True, check if user owns the resource (for update/delete operations)

    Usage:
        @app.route('/posts', methods=['POST'])
        @require_auth
        @require_permission('create', 'post')
        def create_post():
            return jsonify({'message': 'Post created'})

        @app.route('/posts/<int:post_id>', methods=['PUT'])
        @require_auth
        @require_permission('update', 'post', check_ownership=True)
        def update_post(post_id):
            return jsonify({'message': 'Post updated'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()

            if not user:
                return jsonify({
                    'error': MSG_AUTH_REQUIRED,
                    'message': MSG_LOGIN_REQUIRED,
                }), 401

            rbac = g.rbac
            storage = g.storage

            # Resolve resource for ownership checks
            resource = None
            if check_ownership:
                resource, err = _fetch_owned_resource(storage, resource_type, kwargs)
                if err is not None:
                    return err

            try:
                context = _build_permission_context(user, resource)
                rbac_user_id = f"user_{user['user_id']}"
                can_access = rbac.can(
                    user_id=rbac_user_id,
                    action=action,
                    resource=resource_type,
                    context=context,
                )

                if not can_access:
                    return _forbidden_response(check_ownership, resource, context, action, resource_type)

                # Ownership enforcement: if the resource is found and the user does not
                # own it, only override roles (admin/editor) may proceed.
                if (
                    check_ownership
                    and resource
                    and not context.get('is_owner')
                    and user.get('role', '') not in OWNERSHIP_OVERRIDE_ROLES
                ):
                    return _forbidden_response(True, resource, context, action, resource_type)

                if resource:
                    g.resource = resource

                return f(*args, **kwargs)

            except Exception as e:
                logger.error('Authorization check failed: %s', str(e), exc_info=True)
                return jsonify({
                    'error': 'Authorization error',
                    'message': 'Failed to check permissions',
                }), 500

        return decorated_function
    return decorator


def require_role(*roles):
    """
    Decorator to require specific role(s) for a route.
    User must have at least one of the specified roles.
    
    Args:
        *roles: One or more role names (e.g., 'admin', 'editor')
    
    Usage:
        @app.route('/admin/users')
        @require_auth
        @require_role('admin')
        def list_users():
            # Only admins can access
            return jsonify({'users': all_users})
        
        @app.route('/moderate')
        @require_auth
        @require_role('admin', 'editor')
        def moderate_content():
            # Admins or editors can access
            return jsonify({'message': 'Moderation panel'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({
                    'error': MSG_AUTH_REQUIRED,
                    'message': MSG_LOGIN_REQUIRED
                }), 401
            
            user_role = user.get('role', '')
            
            if user_role not in roles:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'This action requires one of these roles: {", ".join(roles)}',
                    'your_role': user_role
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_admin(f):
    """
    Decorator to require admin role for a route.
    Shorthand for @require_role('admin').
    
    Usage:
        @app.route('/admin/stats')
        @require_auth
        @require_admin
        def admin_stats():
            return jsonify({'stats': system_stats})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            return jsonify({
                'error': MSG_AUTH_REQUIRED,
                'message': MSG_LOGIN_REQUIRED
            }), 401
        
        if user.get('role') != 'admin':
            return jsonify({
                'error': 'Forbidden',
                'message': 'This action requires admin privileges',
                'your_role': user.get('role')
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
