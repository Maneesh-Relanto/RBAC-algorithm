"""
Flask Blog API - Main Application
A complete REST API demonstrating RBAC Algorithm integration.
"""
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from datetime import datetime, timezone

# Local imports
from config import get_config
from auth import AuthManager, require_auth, optional_auth
from decorators import require_permission, require_role, require_admin
from storage import InMemoryStorage
from models import PostStatus

# RBAC imports
from rbac import RBAC

# Constants for error messages
ERROR_NOT_FOUND = 'Not found'
ERROR_VALIDATION = 'Validation error'
MSG_POST_NOT_FOUND = 'Post not found'
MSG_AUTH_REQUIRED = 'Authentication required'
MSG_LOGIN_REQUIRED = 'You must be logged in to perform this action'


def create_app(config_name='development'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize storage
    storage = InMemoryStorage()
    
    # Initialize RBAC (using in-memory storage)
    rbac = RBAC(storage='memory')
    
    # Initialize auth manager
    auth_manager = AuthManager(app.config)
    
    # Store instances for access in routes
    app.storage = storage
    app.rbac = rbac
    app.auth_manager = auth_manager
    
    # Setup RBAC roles and permissions
    setup_rbac(rbac)
    
    # Load seed data
    from seed_data import load_seed_data
    load_seed_data(storage, rbac, auth_manager)
    
    # ==================== Before Request ====================
    
    @app.before_request
    def before_request():
        """Set up request context."""
        g.storage = storage
        g.rbac = rbac
        g.auth_manager = auth_manager
    
    # ==================== Error Handlers ====================
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': ERROR_NOT_FOUND,
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    # ==================== Health Check ====================
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config['API_VERSION']
        })
    
    @app.route('/', methods=['GET'])
    def index():
        """API information."""
        return jsonify({
            'name': app.config['API_TITLE'],
            'version': app.config['API_VERSION'],
            'description': app.config['API_DESCRIPTION'],
            'endpoints': {
                'auth': '/auth/*',
                'posts': '/posts',
                'comments': '/posts/<id>/comments',
                'admin': '/admin/*',
                'health': '/health'
            }
        })
    
    # ==================== Authentication Routes ====================
    
    @app.route('/auth/register', methods=['POST'])
    def register():
        """Register a new user."""
        data = request.get_json()
        
        # Validate input
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'reader').lower()
        
        if not username or not email or not password:
            return jsonify({
                'error': 'Validation error',
                'message': 'Username, email, and password are required'
            }), 400
        
        # Validate role
        valid_roles = ['admin', 'editor', 'author', 'reader']
        if role not in valid_roles:
            return jsonify({
                'error': 'Validation error',
                'message': f'Role must be one of: {", ".join(valid_roles)}'
            }), 400
        
        # Check if username or email already exists
        if storage.get_user_by_username(username):
            return jsonify({
                'error': 'Conflict',
                'message': 'Username already exists'
            }), 409
        
        if storage.get_user_by_email(email):
            return jsonify({
                'error': 'Conflict',
                'message': 'Email already exists'
            }), 409
        
        # Create user
        password_hash = auth_manager.hash_password(password)
        user = storage.create_user(username, email, password_hash, role)
        
        # Add user to RBAC system
        rbac.create_user(
            user_id=f"user_{user.id}",
            email=user.email,
            name=user.username
        )
        rbac.assign_role(f"user_{user.id}", f"role_{role}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_public_dict()
        }), 201
    
    @app.route('/auth/login', methods=['POST'])
    def login():
        """Login and get JWT token."""
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'error': 'Validation error',
                'message': 'Username and password are required'
            }), 400
        
        # Get user
        user = storage.get_user_by_username(username)
        
        if not user or not auth_manager.verify_password(password, user.password_hash):
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid username or password'
            }), 401
        
        # Generate token
        token = auth_manager.generate_token(user.id, user.username, user.role)
        
        return jsonify({
            'token': token,
            'user': user.to_public_dict(),
            'expires_in': int(app.config['JWT_EXPIRATION'].total_seconds())
        })
    
    @app.route('/auth/me', methods=['GET'])
    @require_auth
    def get_current_user():
        """Get current user info."""
        user = g.current_user
        user_data = storage.get_user(user['user_id'])
        
        if not user_data:
            return jsonify({
                'error': ERROR_NOT_FOUND,
                'message': 'User not found'
            }), 404
        
        return jsonify(user_data.to_dict())
    
    # ==================== Post Routes ====================
    
    @app.route('/posts', methods=['GET'])
    @optional_auth
    def list_posts():
        """List all posts (public or filtered)."""
        # Anonymous users see only published posts
        # Authenticated users see all their posts + published posts from others
        
        current_user = g.current_user
        
        if current_user:
            # Get user's own posts (all statuses)
            own_posts = storage.list_posts(author_id=current_user['user_id'])
            # Get other's published posts
            all_posts = storage.list_posts(status=PostStatus.PUBLISHED)
            
            # Combine and deduplicate
            post_ids = set()
            posts = []
            for post in own_posts + all_posts:
                if post.id not in post_ids:
                    post_ids.add(post.id)
                    posts.append(post)
            
            # Sort by created_at descending
            posts.sort(key=lambda p: p.created_at, reverse=True)
        else:
            # Only published posts for anonymous users
            posts = storage.list_posts(status=PostStatus.PUBLISHED)
        
        return jsonify({
            'posts': [p.to_summary_dict() for p in posts],
            'count': len(posts)
        })
    
    @app.route('/posts/<int:post_id>', methods=['GET'])
    @optional_auth
    def get_post(post_id):
        """Get a specific post."""
        post = storage.get_post(str(post_id))
        
        if not post:
            return jsonify({
                'error': 'Not found',
                'message': 'Post not found'
            }), 404
        
        # Check if user can view this post
        current_user = g.current_user
        
        # Published posts are public
        if post.status == PostStatus.PUBLISHED:
            return jsonify(post.to_dict())
        
        # Non-published posts require ownership
        if not current_user or current_user['user_id'] != post.author_id:
            return jsonify({
                'error': 'Forbidden',
                'message': 'You do not have permission to view this post'
            }), 403
        
        return jsonify(post.to_dict())
    
    @app.route('/posts', methods=['POST'])
    @require_auth
    @require_permission('create', 'post')
    def create_post():
        """Create a new post."""
        data = request.get_json()
        user = g.current_user
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        status = data.get('status', 'draft').lower()
        tags = data.get('tags', [])
        
        if not title or not content:
            return jsonify({
                'error': 'Validation error',
                'message': 'Title and content are required'
            }), 400
        
        # Validate status
        try:
            status_enum = PostStatus(status)
        except ValueError:
            return jsonify({
                'error': 'Validation error',
                'message': f'Invalid status. Must be one of: {", ".join([s.value for s in PostStatus])}'
            }), 400
        
        # Create post
        post = storage.create_post(
            title=title,
            content=content,
            author_id=user['user_id'],
            author_username=user['username'],
            status=status_enum,
            tags=tags
        )
        
        return jsonify({
            'message': 'Post created successfully',
            'post': post.to_dict()
        }), 201
    
    @app.route('/posts/<int:post_id>', methods=['PUT'])
    @require_auth
    @require_permission('update', 'post', check_ownership=True)
    def update_post(post_id):
        """Update a post (must be owner or editor/admin)."""
        data = request.get_json()
        # Resource validated by decorator
        
        title = data.get('title')
        content = data.get('content')
        status = data.get('status')
        tags = data.get('tags')
        
        # Validate status if provided
        status_enum = None
        if status:
            try:
                status_enum = PostStatus(status.lower())
            except ValueError:
                return jsonify({
                    'error': 'Validation error',
                    'message': f'Invalid status. Must be one of: {", ".join([s.value for s in PostStatus])}'
                }), 400
        
        # Update post
        updated_post = storage.update_post(
            str(post_id),
            title=title,
            content=content,
            status=status_enum,
            tags=tags
        )
        
        return jsonify({
            'message': 'Post updated successfully',
            'post': updated_post.to_dict()
        })
    
    @app.route('/posts/<int:post_id>', methods=['DELETE'])
    @require_auth
    @require_permission('delete', 'post', check_ownership=True)
    def delete_post(post_id):
        """Delete a post (must be owner or editor/admin)."""
        success = storage.delete_post(str(post_id))
        
        if success:
            return jsonify({
                'message': 'Post deleted successfully'
            })
        
        return jsonify({
            'error': 'Not found',
            'message': 'Post not found'
        }), 404
    
    @app.route('/posts/<int:post_id>/publish', methods=['POST'])
    @require_auth
    @require_permission('publish', 'post')
    def publish_post(post_id):
        """Publish a post (requires publish permission)."""
        post = storage.get_post(str(post_id))
        
        if not post:
            return jsonify({
                'error': 'Not found',
                'message': 'Post not found'
            }), 404
        
        # Update to published
        updated_post = storage.update_post(str(post_id), status=PostStatus.PUBLISHED)
        
        return jsonify({
            'message': 'Post published successfully',
            'post': updated_post.to_dict()
        })
    
    # ==================== Comment Routes ====================
    
    @app.route('/posts/<int:post_id>/comments', methods=['GET'])
    def list_comments(post_id):
        """List comments for a post."""
        # Check if post exists
        post = storage.get_post(str(post_id))
        if not post:
            return jsonify({
                'error': 'Not found',
                'message': 'Post not found'
            }), 404
        
        comments = storage.list_comments(str(post_id))
        
        return jsonify({
            'comments': [c.to_dict() for c in comments],
            'count': len(comments)
        })
    
    @app.route('/posts/<int:post_id>/comments', methods=['POST'])
    @require_auth
    @require_permission('create', 'comment')
    def create_comment(post_id):
        """Add a comment to a post."""
        data = request.get_json()
        user = g.current_user
        
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'error': 'Validation error',
                'message': 'Content is required'
            }), 400
        
        comment = storage.create_comment(
            post_id=str(post_id),
            content=content,
            author_id=user['user_id'],
            author_username=user['username']
        )
        
        if not comment:
            return jsonify({
                'error': 'Not found',
                'message': 'Post not found'
            }), 404
        
        return jsonify({
            'message': 'Comment created successfully',
            'comment': comment.to_dict()
        }), 201
    
    @app.route('/comments/<int:comment_id>', methods=['DELETE'])
    @require_auth
    @require_permission('delete', 'comment', check_ownership=True)
    def delete_comment(comment_id):
        """Delete a comment (must be owner or moderator)."""
        success = storage.delete_comment(str(comment_id), soft=True)
        
        if success:
            return jsonify({
                'message': 'Comment deleted successfully'
            })
        
        return jsonify({
            'error': 'Not found',
            'message': 'Comment not found'
        }), 404
    
    # ==================== Admin Routes ====================
    
    @app.route('/admin/users', methods=['GET'])
    @require_auth
    @require_admin
    def list_users():
        """List all users (admin only)."""
        users = storage.list_users()
        
        return jsonify({
            'users': [u.to_dict() for u in users],
            'count': len(users)
        })
    
    @app.route('/admin/users/<int:user_id>/role', methods=['PUT'])
    @require_auth
    @require_admin
    def update_user_role(user_id):
        """Update a user's role (admin only)."""
        data = request.get_json()
        new_role = data.get('role', '').lower()
        
        valid_roles = ['admin', 'editor', 'author', 'reader']
        if new_role not in valid_roles:
            return jsonify({
                'error': 'Validation error',
                'message': f'Role must be one of: {", ".join(valid_roles)}'
            }), 400
        
        user = storage.update_user_role(str(user_id), new_role)
        
        if not user:
            return jsonify({
                'error': 'Not found',
                'message': 'User not found'
            }), 404
        
        # Update RBAC role - remove old role and assign new one
        rbac_user_id = f"user_{user_id}"
        try:
            # Get current roles
            user_details = rbac.get_user(rbac_user_id)
            if user_details:
                # Note: The RBAC library should have revoke_role
                # by reassigning - the library should handle this internally
                pass
            
            # Assign new role
            rbac.assign_role(rbac_user_id, f"role_{new_role}")
        except Exception:
            # If user doesn't exist in RBAC, create them
            try:
                rbac.create_user(
                    user_id=rbac_user_id,
                    email=user.email,
                    name=user.username
                )
                rbac.assign_role(rbac_user_id, f"role_{new_role}")
            except Exception:
                pass  # User might already exist
        
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        })
    
    @app.route('/admin/stats', methods=['GET'])
    @require_auth
    @require_admin
    def get_stats():
        """Get system statistics (admin only)."""
        stats = storage.get_stats()
        
        return jsonify(stats.to_dict())
    
    return app


def setup_rbac(rbac: RBAC):
    """Set up RBAC roles and permissions."""
    
    # Define permissions
    permissions_data = [
        # Post permissions
        ('perm_post_create', 'post', 'create', 'Create blog posts'),
        ('perm_post_read', 'post', 'read', 'Read blog posts'),
        ('perm_post_update', 'post', 'update', 'Update blog posts'),
        ('perm_post_delete', 'post', 'delete', 'Delete blog posts'),
        ('perm_post_publish', 'post', 'publish', 'Publish blog posts'),
        
        # Comment permissions
        ('perm_comment_create', 'comment', 'create', 'Create comments'),
        ('perm_comment_read', 'comment', 'read', 'Read comments'),
        ('perm_comment_delete', 'comment', 'delete', 'Delete comments'),
        
        # User permissions
        ('perm_user_manage', 'user', 'manage', 'Manage users'),
        ('perm_stats_view', 'stats', 'view', 'View statistics'),
    ]
    
    for perm_id, resource_type, action, description in permissions_data:
        rbac.create_permission(
            permission_id=perm_id,
            resource_type=resource_type,
            action=action,
            description=description
        )
    
    # Define roles and their permissions
    roles_data = {
        'admin': {
            'name': 'Administrator',
            'permissions': [
                'perm_post_create', 'perm_post_read', 'perm_post_update',
                'perm_post_delete', 'perm_post_publish',
                'perm_comment_create', 'perm_comment_read', 'perm_comment_delete',
                'perm_user_manage', 'perm_stats_view'
            ],
            'description': 'Full access to all resources'
        },
        'editor': {
            'name': 'Editor',
            'permissions': [
                'perm_post_create', 'perm_post_read', 'perm_post_update',
                'perm_post_delete', 'perm_post_publish',
                'perm_comment_create', 'perm_comment_read', 'perm_comment_delete'
            ],
            'description': 'Can manage all content'
        },
        'author': {
            'name': 'Author',
            'permissions': [
                'perm_post_create', 'perm_post_read', 'perm_post_update', 'perm_post_delete',
                'perm_comment_create', 'perm_comment_read'
            ],
            'description': 'Can create and manage own posts'
        },
        'reader': {
            'name': 'Reader',
            'permissions': [
                'perm_post_read', 'perm_comment_read', 'perm_comment_create'
            ],
            'description': 'Can read content and add comments'
        }
    }
    
    for role_id, role_data in roles_data.items():
        rbac.create_role(
            role_id=f'role_{role_id}',
            name=role_data['name'],
            permissions=role_data['permissions'],
            description=role_data['description']
        )


if __name__ == '__main__':
    app = create_app('development')
    print("""
    ╔════════════════════════════════════════════════╗
    ║   Flask Blog API - RBAC Test Application      ║
    ╠════════════════════════════════════════════════╣
    ║                                                ║
    ║   🚀 Server starting...                        ║
    ║   📍 URL: http://localhost:5000                ║
    ║   📖 Docs: See README.md for usage examples    ║
    ║                                                ║
    ║   Sample users loaded:                         ║
    ║   - admin / admin123 (admin)                   ║
    ║   - editor / editor123 (editor)                ║
    ║   - john_author / author123 (author)           ║
    ║   - jane_reader / reader123 (reader)           ║
    ║                                                ║
    ╚════════════════════════════════════════════════╝
    """)
    # Use debug flag from app config (controlled via FLASK_DEBUG env var) rather than
    # hardcoding debug=True, which would enable the interactive debugger in production.
    app.run(debug=app.config.get('DEBUG', False), host='0.0.0.0', port=5000)
