"""
JWT Authentication module for Flask Blog API.
Handles user authentication, token generation, and verification.
"""
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from config import Config


class AuthManager:
    """Manages JWT authentication operations."""
    
    def __init__(self, config):
        """Initialize auth manager with configuration."""
        self.secret_key = config['JWT_SECRET_KEY']
        self.algorithm = config['JWT_ALGORITHM']
        self.expiration = config['JWT_EXPIRATION']
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: str, username: str, role: str) -> str:
        """Generate a JWT token for a user."""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + self.expiration
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def decode_token(self, token: str) -> dict:
        """
        Decode and verify a JWT token.
        
        Returns:
            dict: Token payload if valid
            
        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
        """
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload
    
    def extract_token_from_header(self) -> str | None:
        """
        Extract JWT token from Authorization header.
        
        Returns:
            str | None: Token string or None if not found
        """
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None


def require_auth(f):
    """
    Decorator to require authentication for a route.
    Extracts user info from JWT and stores in Flask's g object.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user = g.current_user
            return jsonify({'user': user})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_manager = g.auth_manager
        token = auth_manager.extract_token_from_header()
        
        if not token:
            return jsonify({
                'error': 'Authentication required',
                'message': 'No token provided'
            }), 401
        
        try:
            payload = auth_manager.decode_token(token)
            
            # Store user info in Flask's g object
            g.current_user = {
                'user_id': payload['user_id'],
                'username': payload['username'],
                'role': payload['role']
            }
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({
                'error': 'Token expired',
                'message': 'Please login again'
            }), 401
            
        except jwt.InvalidTokenError:
            # Do not expose internal JWT error details to the client
            return jsonify({
                'error': 'Invalid token',
                'message': 'Token is invalid'
            }), 401
    
    return decorated_function


def optional_auth(f):
    """
    Decorator that allows optional authentication.
    If token is present and valid, user info is stored in g.current_user.
    If not, g.current_user is None.
    
    Useful for endpoints that work differently for authenticated users.
    
    Usage:
        @app.route('/posts')
        @optional_auth
        def list_posts():
            if g.current_user:
                # Show all posts including drafts for authenticated users
                return jsonify({'posts': all_posts})
            else:
                # Show only published posts for anonymous users
                return jsonify({'posts': published_posts})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_manager = g.auth_manager
        token = auth_manager.extract_token_from_header()
        
        if token:
            try:
                payload = auth_manager.decode_token(token)
                g.current_user = {
                    'user_id': payload['user_id'],
                    'username': payload['username'],
                    'role': payload['role']
                }
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                # Invalid token, but continue without auth
                g.current_user = None
        else:
            g.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    Helper function to get current authenticated user.
    
    Returns:
        dict: User info or None if not authenticated
    """
    return getattr(g, 'current_user', None)
