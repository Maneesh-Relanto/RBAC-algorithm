"""
JWT Authentication module for FastAPI Blog API.
Uses FastAPI's Dependency Injection instead of Flask's g/decorators.
"""
import logging
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import Settings

logger = logging.getLogger(__name__)

# HTTPBearer with auto_error=False so optional auth returns None instead of 401
_bearer_scheme = HTTPBearer(auto_error=False)


class AuthManager:
    """Manages JWT authentication operations."""

    def __init__(self, cfg: Settings) -> None:
        self.secret_key = cfg.JWT_SECRET_KEY
        self.algorithm = cfg.JWT_ALGORITHM
        self.expiration = cfg.JWT_EXPIRATION

    # ------------------------------------------------------------------
    # Password helpers
    # ------------------------------------------------------------------

    def hash_password(self, password: str) -> str:
        """Hash a plain-text password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a plain-text password against its bcrypt hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    # ------------------------------------------------------------------
    # Token helpers
    # ------------------------------------------------------------------

    def generate_token(self, user_id: str, username: str, role: str) -> str:
        """Generate a signed JWT for the given user."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,
            "iat": now,
            "exp": now + self.expiration,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """
        Decode and verify a JWT.

        Raises:
            jwt.ExpiredSignatureError: token has expired
            jwt.InvalidTokenError: token is otherwise invalid
        """
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])


# ---------------------------------------------------------------------------
# FastAPI dependency: retrieve AuthManager from app.state
# ---------------------------------------------------------------------------

def get_auth_manager(request: Request) -> AuthManager:
    """FastAPI dependency — returns the shared AuthManager instance."""
    return request.app.state.auth_manager


# ---------------------------------------------------------------------------
# FastAPI dependency: required authentication
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> dict:
    """
    FastAPI dependency that requires a valid Bearer token.

    Returns the decoded token payload as a dict::

        {"user_id": "1", "username": "alice", "role": "author"}

    Raises:
        HTTPException 401 – if no token, expired, or invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Authentication required", "message": "No token provided"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = auth_manager.decode_token(token)
        return {
            "user_id": payload["user_id"],
            "username": payload["username"],
            "role": payload["role"],
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Token expired", "message": "Please login again"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        # Do not expose internal JWT error details to the client
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid token", "message": "Token is invalid"},
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# FastAPI dependency: optional authentication
# ---------------------------------------------------------------------------

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    auth_manager: AuthManager = Depends(get_auth_manager),
) -> Optional[dict]:
    """
    FastAPI dependency that accepts an optional Bearer token.

    Returns the payload dict when a valid token is present, otherwise None.
    Invalid/expired tokens are silently ignored.
    """
    if credentials is None:
        return None
    try:
        payload = auth_manager.decode_token(credentials.credentials)
        return {
            "user_id": payload["user_id"],
            "username": payload["username"],
            "role": payload["role"],
        }
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
