"""
RBAC Decorators for Flask Blog API.
Provides decorators for permission and role-based authorization.
"""
from functools import wraps
from flask import g, jsonify
from auth import get_current_user


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
            # User has 'create:post' permission
            return jsonify({'message': 'Post created'})
        
        @app.route('/posts/<int:post_id>', methods=['PUT'])
        @require_auth
        @require_permission('update', 'post', check_ownership=True)
        def update_post(post_id):
            # User has 'update:post' permission AND owns the post
            return jsonify({'message': 'Post updated'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            
            if not user:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'You must be logged in to perform this action'
                }), 401
            
            # Get RBAC engine from Flask's g object
            rbac = g.rbac
            storage = g.storage
            
            # Build permission string
            permission = f"{action}:{resource_type}" if resource_type else action
            
            # Get resource for ownership check
            resource = None
            if check_ownership:
                # Extract resource ID from URL parameters
                resource_id = kwargs.get('post_id') or kwargs.get('comment_id') or kwargs.get('id')
                
                if resource_id:
                    # Get resource from storage to check ownership
                    if 'post' in (resource_type or ''):
                        resource = storage.get_post(resource_id)
                    elif 'comment' in (resource_type or ''):
                        resource = storage.get_comment(resource_id)
                    
                    if not resource:
                        return jsonify({
                            'error': 'Not found',
                            'message': f'{resource_type.capitalize()} not found'
                        }), 404
            
            # Check permission with RBAC engine
            try:
                # Build context for ABAC (attribute-based) checks
                context = {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role']
                }
                
                # Add resource info to context for ownership checks
                if resource:
                    context['resource_owner'] = getattr(resource, 'author_id', None) or getattr(resource, 'user_id', None)
                    context['is_owner'] = context['resource_owner'] == user['user_id']
                
                # Perform authorization check using user_id with 'user_' prefix
                rbac_user_id = f"user_{user['user_id']}"
                can_access = rbac.can(
                    user_id=rbac_user_id,
                    action=action,
                    resource=resource_type,
                    context=context
                )
                
                if not can_access:
                    # If ownership check required but user doesn't own the resource
                    if check_ownership and resource and not context.get('is_owner'):
                        return jsonify({
                            'error': 'Forbidden',
                            'message': 'You can only modify your own content',
                            'reason': 'ownership_required'
                        }), 403
                    
                    return jsonify({
                        'error': 'Forbidden',
                        'message': f'You do not have permission to {action} {resource_type}',
                        'reason': 'permission_denied'
                    }), 403
                
                # Store resource in g for handler use
                if resource:
                    g.resource = resource
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'error': 'Authorization error',
                    'message': f'Failed to check permissions: {str(e)}'
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
                    'error': 'Authentication required',
                    'message': 'You must be logged in to perform this action'
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
                'error': 'Authentication required',
                'message': 'You must be logged in to perform this action'
            }), 401
        
        if user.get('role') != 'admin':
            return jsonify({
                'error': 'Forbidden',
                'message': 'This action requires admin privileges',
                'your_role': user.get('role')
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
