"""
Flask Blog API - Main Application
A complete REST API demonstrating RBAC Algorithm integration.
"""
from datetime import datetime, timezone

from flask import Blueprint, Flask, current_app, g, jsonify, request
from flask_cors import CORS

# Local imports
from auth import AuthManager, optional_auth, require_auth
from config import get_config
from decorators import require_permission, require_admin
from models import PostStatus
from storage import InMemoryStorage

# RBAC imports
from rbac import RBAC

# Constants for error messages
ERROR_NOT_FOUND = 'Not found'
ERROR_VALIDATION = 'Validation error'
MSG_POST_NOT_FOUND = 'Post not found'
MSG_AUTH_REQUIRED = 'Authentication required'
MSG_LOGIN_REQUIRED = 'You must be logged in to perform this action'

# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
posts_bp = Blueprint('posts', __name__, url_prefix='/posts')
comments_bp = Blueprint('comments', __name__, url_prefix='/comments')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
VALID_ROLES = ['admin', 'editor', 'author', 'reader']


def _not_found(msg='The requested resource was not found'):
    return jsonify({'error': ERROR_NOT_FOUND, 'message': msg}), 404


def _validation_error(msg):
    return jsonify({'error': ERROR_VALIDATION, 'message': msg}), 400


# ---------------------------------------------------------------------------
# Main routes
# ---------------------------------------------------------------------------

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': current_app.config['API_VERSION'],
    })


@main_bp.route('/', methods=['GET'])
def index():
    """API information."""
    return jsonify({
        'name': current_app.config['API_TITLE'],
        'version': current_app.config['API_VERSION'],
        'description': current_app.config['API_DESCRIPTION'],
        'endpoints': {
            'auth': '/auth/*',
            'posts': '/posts',
            'comments': '/posts/<id>/comments',
            'admin': '/admin/*',
            'health': '/health',
        },
    })


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'reader').lower()

    if not username or not email or not password:
        return _validation_error('Username, email, and password are required')

    if role not in VALID_ROLES:
        return _validation_error(f'Role must be one of: {", ".join(VALID_ROLES)}')

    storage = g.storage
    if storage.get_user_by_username(username):
        return jsonify({'error': 'Conflict', 'message': 'Username already exists'}), 409

    if storage.get_user_by_email(email):
        return jsonify({'error': 'Conflict', 'message': 'Email already exists'}), 409

    auth_manager = g.auth_manager
    password_hash = auth_manager.hash_password(password)
    user = storage.create_user(username, email, password_hash, role)

    rbac = g.rbac
    rbac.create_user(user_id=f"user_{user.id}", email=user.email, name=user.username)
    rbac.assign_role(f"user_{user.id}", f"role_{role}")

    return jsonify({'message': 'User registered successfully', 'user': user.to_public_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get JWT token."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return _validation_error('Username and password are required')

    storage = g.storage
    auth_manager = g.auth_manager
    user = storage.get_user_by_username(username)

    if not user or not auth_manager.verify_password(password, user.password_hash):
        return jsonify({'error': 'Authentication failed', 'message': 'Invalid username or password'}), 401

    token = auth_manager.generate_token(user.id, user.username, user.role)
    return jsonify({
        'token': token,
        'user': user.to_public_dict(),
        'expires_in': int(current_app.config['JWT_EXPIRATION'].total_seconds()),
    })


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user_info():
    """Get current user info."""
    user = g.current_user
    user_data = g.storage.get_user(user['user_id'])
    if not user_data:
        return _not_found('User not found')
    return jsonify(user_data.to_dict())


# ---------------------------------------------------------------------------
# Post routes
# ---------------------------------------------------------------------------

@posts_bp.route('', methods=['GET'])
@optional_auth
def list_posts():
    """List all posts."""
    storage = g.storage
    current_user = g.current_user

    if current_user:
        own_posts = storage.list_posts(author_id=current_user['user_id'])
        all_published = storage.list_posts(status=PostStatus.PUBLISHED)
        seen = set()
        posts = []
        for post in own_posts + all_published:
            if post.id not in seen:
                seen.add(post.id)
                posts.append(post)
        posts.sort(key=lambda p: p.created_at, reverse=True)
    else:
        posts = storage.list_posts(status=PostStatus.PUBLISHED)

    return jsonify({'posts': [p.to_summary_dict() for p in posts], 'count': len(posts)})


@posts_bp.route('/<int:post_id>', methods=['GET'])
@optional_auth
def get_post(post_id):
    """Get a specific post."""
    post = g.storage.get_post(str(post_id))
    if not post:
        return _not_found('Post not found')

    if post.status == PostStatus.PUBLISHED:
        return jsonify(post.to_dict())

    current_user = g.current_user
    if not current_user or current_user['user_id'] != post.author_id:
        return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to view this post'}), 403

    return jsonify(post.to_dict())


@posts_bp.route('', methods=['POST'])
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
        return _validation_error('Title and content are required')

    try:
        status_enum = PostStatus(status)
    except ValueError:
        return _validation_error(f'Invalid status. Must be one of: {", ".join(s.value for s in PostStatus)}')

    post = g.storage.create_post(
        title=title,
        content=content,
        author_id=user['user_id'],
        author_username=user['username'],
        status=status_enum,
        tags=tags,
    )
    return jsonify({'message': 'Post created successfully', 'post': post.to_dict()}), 201


@posts_bp.route('/<int:post_id>', methods=['PUT'])
@require_auth
@require_permission('update', 'post', check_ownership=True)
def update_post(post_id):
    """Update a post."""
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    status = data.get('status')
    tags = data.get('tags')

    status_enum = None
    if status:
        try:
            status_enum = PostStatus(status.lower())
        except ValueError:
            return _validation_error(f'Invalid status. Must be one of: {", ".join(s.value for s in PostStatus)}')

    updated_post = g.storage.update_post(
        str(post_id), title=title, content=content, status=status_enum, tags=tags
    )
    return jsonify({'message': 'Post updated successfully', 'post': updated_post.to_dict()})


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@require_auth
@require_permission('delete', 'post', check_ownership=True)
def delete_post(post_id):
    """Delete a post."""
    if g.storage.delete_post(str(post_id)):
        return jsonify({'message': 'Post deleted successfully'})
    return _not_found('Post not found')


@posts_bp.route('/<int:post_id>/publish', methods=['POST'])
@require_auth
@require_permission('publish', 'post')
def publish_post(post_id):
    """Publish a post."""
    post = g.storage.get_post(str(post_id))
    if not post:
        return _not_found('Post not found')
    updated_post = g.storage.update_post(str(post_id), status=PostStatus.PUBLISHED)
    return jsonify({'message': 'Post published successfully', 'post': updated_post.to_dict()})


@posts_bp.route('/<int:post_id>/comments', methods=['GET'])
def list_comments(post_id):
    """List comments for a post."""
    if not g.storage.get_post(str(post_id)):
        return _not_found('Post not found')
    comments = g.storage.list_comments(str(post_id))
    return jsonify({'comments': [c.to_dict() for c in comments], 'count': len(comments)})


@posts_bp.route('/<int:post_id>/comments', methods=['POST'])
@require_auth
@require_permission('create', 'comment')
def create_comment(post_id):
    """Add a comment to a post."""
    data = request.get_json()
    user = g.current_user
    content = data.get('content', '').strip()

    if not content:
        return _validation_error('Content is required')

    comment = g.storage.create_comment(
        post_id=str(post_id),
        content=content,
        author_id=user['user_id'],
        author_username=user['username'],
    )
    if not comment:
        return _not_found('Post not found')
    return jsonify({'message': 'Comment created successfully', 'comment': comment.to_dict()}), 201


# ---------------------------------------------------------------------------
# Comment routes
# ---------------------------------------------------------------------------

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@require_auth
@require_permission('delete', 'comment', check_ownership=True)
def delete_comment(comment_id):
    """Delete a comment."""
    if g.storage.delete_comment(str(comment_id), soft=True):
        return jsonify({'message': 'Comment deleted successfully'})
    return _not_found('Comment not found')


# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@admin_bp.route('/users', methods=['GET'])
@require_auth
@require_admin
def list_users():
    """List all users (admin only)."""
    users = g.storage.list_users()
    return jsonify({'users': [u.to_dict() for u in users], 'count': len(users)})


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@require_auth
@require_admin
def update_user_role(user_id):
    """Update a user's role (admin only)."""
    data = request.get_json()
    new_role = data.get('role', '').lower()

    if new_role not in VALID_ROLES:
        return _validation_error(f'Role must be one of: {", ".join(VALID_ROLES)}')

    user = g.storage.update_user_role(str(user_id), new_role)
    if not user:
        return _not_found('User not found')

    rbac = g.rbac
    rbac_user_id = f"user_{user_id}"
    try:
        rbac.assign_role(rbac_user_id, f"role_{new_role}")
    except Exception:
        try:
            rbac.create_user(user_id=rbac_user_id, email=user.email, name=user.username)
            rbac.assign_role(rbac_user_id, f"role_{new_role}")
        except Exception:
            pass  # User might already exist with the role

    return jsonify({'message': 'User role updated successfully', 'user': user.to_dict()})


@admin_bp.route('/stats', methods=['GET'])
@require_auth
@require_admin
def get_stats():
    """Get system statistics (admin only)."""
    return jsonify(g.storage.get_stats().to_dict())


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(config_name='development'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    CORS(app, origins=app.config['CORS_ORIGINS'])

    storage = InMemoryStorage()
    rbac = RBAC(storage='memory')
    auth_manager = AuthManager(app.config)

    # Store on app for test-client access
    app.storage = storage
    app.rbac = rbac
    app.auth_manager = auth_manager

    setup_rbac(rbac)

    from seed_data import load_seed_data
    load_seed_data(storage, rbac, auth_manager)

    @app.before_request
    def _push_to_g():
        g.storage = storage
        g.rbac = rbac
        g.auth_manager = auth_manager

    @app.errorhandler(404)
    def _not_found_handler(error):  # noqa: ARG001
        return jsonify({'error': ERROR_NOT_FOUND, 'message': 'The requested resource was not found'}), 404

    @app.errorhandler(500)
    def _server_error_handler(error):  # noqa: ARG001
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(admin_bp)

    return app


# ---------------------------------------------------------------------------
# RBAC setup
# ---------------------------------------------------------------------------

def setup_rbac(rbac: RBAC):
    """Set up RBAC roles and permissions."""
    permissions_data = [
        ('perm_post_create', 'post', 'create', 'Create blog posts'),
        ('perm_post_read', 'post', 'read', 'Read blog posts'),
        ('perm_post_update', 'post', 'update', 'Update blog posts'),
        ('perm_post_delete', 'post', 'delete', 'Delete blog posts'),
        ('perm_post_publish', 'post', 'publish', 'Publish blog posts'),
        ('perm_comment_create', 'comment', 'create', 'Create comments'),
        ('perm_comment_read', 'comment', 'read', 'Read comments'),
        ('perm_comment_delete', 'comment', 'delete', 'Delete comments'),
        ('perm_user_manage', 'user', 'manage', 'Manage users'),
        ('perm_stats_view', 'stats', 'view', 'View statistics'),
    ]
    for perm_id, resource_type, action, description in permissions_data:
        rbac.create_permission(
            permission_id=perm_id,
            resource_type=resource_type,
            action=action,
            description=description,
        )

    roles_data = {
        'admin': {
            'name': 'Administrator',
            'permissions': [
                'perm_post_create', 'perm_post_read', 'perm_post_update',
                'perm_post_delete', 'perm_post_publish',
                'perm_comment_create', 'perm_comment_read', 'perm_comment_delete',
                'perm_user_manage', 'perm_stats_view',
            ],
            'description': 'Full access to all resources',
        },
        'editor': {
            'name': 'Editor',
            'permissions': [
                'perm_post_create', 'perm_post_read', 'perm_post_update',
                'perm_post_delete', 'perm_post_publish',
                'perm_comment_create', 'perm_comment_read', 'perm_comment_delete',
            ],
            'description': 'Can manage all content',
        },
        'author': {
            'name': 'Author',
            'permissions': [
                'perm_post_create', 'perm_post_read', 'perm_post_update', 'perm_post_delete',
                'perm_comment_create', 'perm_comment_read',
            ],
            'description': 'Can create and manage own posts',
        },
        'reader': {
            'name': 'Reader',
            'permissions': ['perm_post_read', 'perm_comment_read', 'perm_comment_create', 'perm_comment_delete'],
            'description': 'Can read content and add comments (including deleting own comments)',
        },
    }
    for role_id, role_data in roles_data.items():
        rbac.create_role(
            role_id=f'role_{role_id}',
            name=role_data['name'],
            permissions=role_data['permissions'],
            description=role_data['description'],
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
    app.run(debug=app.config.get('DEBUG', False), host='0.0.0.0', port=5000)
