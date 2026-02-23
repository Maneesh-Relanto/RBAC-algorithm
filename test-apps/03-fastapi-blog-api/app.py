"""
FastAPI Blog API — Main Application
====================================
A feature-complete blog REST API demonstrating RBAC integration with FastAPI.

Mirrors the Flask test-app (02-flask-blog-api) but uses FastAPI patterns:
  • Pydantic v2 request/response models  → automatic validation + OpenAPI docs
  • Dependency injection via Depends()   → clean, testable route handlers
  • Lifespan context manager            → replaces Flask's before_first_request
  • HTTPBearer authentication           → standard FastAPI auth pattern

Run::

    pip install -r requirements.txt
    python app.py

Or with uvicorn::

    uvicorn app:app --reload --port 8000

Interactive docs available at: http://localhost:8000/docs
"""
import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ── local imports (all in same directory) ──────────────────────────────────
from auth import get_current_user, get_optional_user
from config import Settings, TestingSettings
from dependencies import RequirePermission, RequireRole, get_rbac, get_storage
from models import PostStatus
from schemas import (
    CommentListResponse,
    CommentResponse,
    CreateCommentRequest,
    CreatePostRequest,
    ErrorResponse,
    HealthResponse,
    MessageResponse,
    PostListResponse,
    PostResponse,
    RegisterRequest,
    LoginRequest,
    StatsResponse,
    TokenResponse,
    UpdatePostRequest,
    UpdateRoleRequest,
    UserListResponse,
    UserResponse,
)
from seed_data import load_seed_data
from storage import InMemoryStorage

logger = logging.getLogger(__name__)

# ── RBAC library ────────────────────────────────────────────────────────────
try:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    from rbac import RBAC
except ImportError as e:
    logger.error("Failed to import RBAC library: %s", e)
    sys.exit(1)


# ============================================================================
# RBAC Setup (permissions & roles shared across lifespan calls)
# ============================================================================

def setup_rbac(rbac: RBAC) -> None:
    """Create all roles, permissions, and assign permissions to roles."""

    # ── permissions ─────────────────────────────────────────────────────────
    permissions = [
        ("create", "post",    "Create a blog post"),
        ("read",   "post",    "Read a blog post"),
        ("update", "post",    "Update a blog post"),
        ("delete", "post",    "Delete a blog post"),
        ("publish","post",    "Publish/unpublish a blog post"),
        ("create", "comment", "Add a comment"),
        ("read",   "comment", "Read comments"),
        ("delete", "comment", "Delete a comment"),
        ("manage", "users",   "Manage user accounts"),
        ("view",   "stats",   "View system statistics"),
    ]
    for action, resource, description in permissions:
        perm_id = f"perm_{action}_{resource}"
        try:
            rbac.create_permission(
                permission_id=perm_id,
                resource_type=resource,
                action=action,
                description=description,
            )
        except Exception:
            pass  # May already exist in testing scenarios

    # ── roles ───────────────────────────────────────────────────────────────
    roles = [
        ("role_admin",   "Administrator", "Full access"),
        ("role_editor",  "Editor",        "Manage all content"),
        ("role_author",  "Author",        "Manage own content"),
        ("role_reader",  "Reader",        "Read-only access"),
    ]
    for role_id, name, desc in roles:
        try:
            rbac.create_role(role_id=role_id, name=name, description=desc)
        except Exception:
            pass

    # ── role → permission assignments ───────────────────────────────────────
    role_permissions: dict[str, list[str]] = {
        "role_admin": [
            "perm_create_post", "perm_read_post", "perm_update_post",
            "perm_delete_post", "perm_publish_post",
            "perm_create_comment", "perm_read_comment", "perm_delete_comment",
            "perm_manage_users", "perm_view_stats",
        ],
        "role_editor": [
            "perm_create_post", "perm_read_post", "perm_update_post",
            "perm_delete_post", "perm_publish_post",
            "perm_create_comment", "perm_read_comment", "perm_delete_comment",
            "perm_view_stats",
        ],
        "role_author": [
            "perm_create_post", "perm_read_post", "perm_update_post", "perm_delete_post",
            "perm_create_comment", "perm_read_comment", "perm_delete_comment",
        ],
        "role_reader": [
            "perm_read_post",
            "perm_create_comment", "perm_read_comment",
        ],
    }

    for role_id, perms in role_permissions.items():
        for perm_id in perms:
            try:
                rbac.add_permission_to_role(role_id=role_id, permission_id=perm_id)
            except Exception:
                pass


# ============================================================================
# Application factory
# ============================================================================

def create_app(testing: bool = False) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        testing: When True, uses TestingSettings (no DB state between imports).
    """
    cfg: Settings = TestingSettings() if testing else Settings()

    # ── lifespan: init & teardown at startup / shutdown ─────────────────────
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        storage = InMemoryStorage()
        rbac = RBAC()  # defaults to in-memory storage
        from auth import AuthManager
        auth_manager = AuthManager(cfg)

        # Configure RBAC schema
        setup_rbac(rbac)

        # Store on app.state so dependency functions can access them
        app.state.storage = storage
        app.state.rbac = rbac
        app.state.auth_manager = auth_manager
        app.state.config = cfg

        # Seed with demo data (skipped in unit tests that call this factory
        # with testing=True and then reload their own fixtures)
        if not testing:
            try:
                load_seed_data(storage, rbac, auth_manager)
            except Exception as exc:
                logger.warning("Seed data loading failed (non-fatal): %s", exc)

        logger.info("FastAPI Blog API started (testing=%s)", testing)
        yield

        # Shutdown
        logger.info("FastAPI Blog API shutting down")

    # ── FastAPI instance ─────────────────────────────────────────────────────
    app = FastAPI(
        title="FastAPI Blog API with RBAC",
        description=(
            "A blog REST API demonstrating Role-Based Access Control (RBAC) "
            "using the rbac-algorithm library.  "
            "Interactive docs: /docs | ReDoc: /redoc"
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom exception handlers ────────────────────────────────────────────
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "message": "The requested resource was not found"},
        )

    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=405,
            content={"error": "Method Not Allowed", "message": "This HTTP method is not allowed here"},
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: Exception):
        logger.error("Unhandled error: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "message": "An unexpected error occurred"},
        )

    # ========================================================================
    # Routes
    # ========================================================================

    # ── Health & root ────────────────────────────────────────────────────────

    @app.get("/health", response_model=HealthResponse, tags=["System"])
    async def health_check():
        """Health check — returns service status."""
        return HealthResponse(status="healthy", service="FastAPI Blog API", version="1.0.0")

    @app.get("/", tags=["System"])
    async def root():
        """API information."""
        return {
            "service": "FastAPI Blog API with RBAC",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                "auth":    ["/auth/register", "/auth/login", "/auth/me"],
                "posts":   ["/posts", "/posts/{id}", "/posts/{id}/publish", "/posts/{id}/comments"],
                "comments":["/comments/{id}"],
                "admin":   ["/admin/users", "/admin/users/{id}/role", "/admin/stats"],
            },
        }

    # ── Authentication ───────────────────────────────────────────────────────

    @app.post("/auth/register", response_model=TokenResponse, status_code=201, tags=["Auth"])
    async def register(
        body: RegisterRequest,
        request: Request,
        storage: InMemoryStorage = Depends(get_storage),
        rbac=Depends(get_rbac),
    ):
        """Register a new user account."""
        if storage.get_user_by_username(body.username):
            raise HTTPException(status_code=409, detail={"error": "Conflict", "message": "Username already taken"})
        if storage.get_user_by_email(body.email):
            raise HTTPException(status_code=409, detail={"error": "Conflict", "message": "Email already registered"})

        auth_manager = request.app.state.auth_manager
        pw_hash = auth_manager.hash_password(body.password)
        user = storage.create_user(
            username=body.username,
            email=body.email,
            password_hash=pw_hash,
            role="reader",
        )

        rbac.create_user(user_id=f"user_{user.id}", email=user.email, name=user.username)
        rbac.assign_role(f"user_{user.id}", "role_reader")

        token = auth_manager.generate_token(user.id, user.username, user.role)
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user.id, username=user.username, email=user.email,
                role=user.role, created_at=user.created_at.isoformat(),
            ),
            message="Registration successful",
        )

    @app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
    async def login(
        body: LoginRequest,
        request: Request,
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Log in and receive a JWT access token."""
        user = storage.get_user_by_username(body.username)
        auth_manager = request.app.state.auth_manager
        if not user or not auth_manager.verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail={"error": "Unauthorized", "message": "Invalid credentials"})

        token = auth_manager.generate_token(user.id, user.username, user.role)
        return TokenResponse(
            access_token=token,
            user=UserResponse(
                id=user.id, username=user.username, email=user.email,
                role=user.role, created_at=user.created_at.isoformat(),
            ),
            message="Login successful",
        )

    @app.get("/auth/me", response_model=UserResponse, tags=["Auth"])
    async def get_me(
        current_user: dict = Depends(get_current_user),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Return the currently authenticated user's profile."""
        user = storage.get_user(current_user["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "User not found"})
        return UserResponse(
            id=user.id, username=user.username, email=user.email,
            role=user.role, created_at=user.created_at.isoformat(),
        )

    # ── Posts ────────────────────────────────────────────────────────────────

    @app.get("/posts", response_model=PostListResponse, tags=["Posts"])
    async def list_posts(
        status_filter: Optional[str] = None,
        current_user: Optional[dict] = Depends(get_optional_user),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """
        List blog posts.

        - Unauthenticated users and readers see published posts only.
        - Authors see their own drafts + all published posts.
        - Editors and admins see all posts.
        """
        role = current_user.get("role") if current_user else None

        if role in ("admin", "editor"):
            status_enum = PostStatus(status_filter) if status_filter else None
            posts = storage.list_posts(status=status_enum)
        elif role == "author" and current_user:
            posts_all = storage.list_posts()
            posts = [
                p for p in posts_all
                if p.status == PostStatus.PUBLISHED or p.author_id == current_user["user_id"]
            ]
        else:
            posts = storage.list_posts(status=PostStatus.PUBLISHED)

        return PostListResponse(
            posts=[p.to_summary_dict() for p in posts],
            total=len(posts),
        )

    @app.post("/posts", response_model=PostResponse, status_code=201, tags=["Posts"])
    async def create_post(
        body: CreatePostRequest,
        current_user: dict = Depends(get_current_user),
        _perm: None = Depends(RequirePermission("create", "post")),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Create a new blog post (requires 'create post' permission)."""
        post = storage.create_post(
            title=body.title,
            content=body.content,
            author_id=current_user["user_id"],
            author_username=current_user["username"],
            status=PostStatus(body.status) if body.status else PostStatus.DRAFT,
            tags=body.tags or [],
        )
        return PostResponse(**post.to_dict())

    @app.get("/posts/{post_id}", tags=["Posts"])
    async def get_post(
        post_id: str,
        current_user: Optional[dict] = Depends(get_optional_user),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Get a single post by ID."""
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Post not found"})

        role = current_user.get("role") if current_user else None
        is_owner = current_user and post.author_id == current_user.get("user_id")

        if post.status != PostStatus.PUBLISHED and not (role in ("admin", "editor") or is_owner):
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Post not found"})

        return post.to_dict()

    @app.put("/posts/{post_id}", tags=["Posts"])
    async def update_post(
        post_id: str,
        body: UpdatePostRequest,
        current_user: dict = Depends(get_current_user),
        storage: InMemoryStorage = Depends(get_storage),
        rbac=Depends(get_rbac),
    ):
        """Update a post. Authors can only update their own posts; editors/admins can update any."""
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Post not found"})

        role = current_user.get("role")
        is_owner = post.author_id == current_user["user_id"]

        can_update = rbac.can(
            user_id=f"user_{current_user['user_id']}",
            action="update",
            resource="post",
            context={
                "user_id": current_user["user_id"],
                "role": role,
                "resource_owner": post.author_id,
                "is_owner": is_owner,
            },
        )
        if not can_update:
            raise HTTPException(
                status_code=403,
                detail={"error": "Forbidden", "message": "You do not have permission to update this post"},
            )

        updates: dict = {}
        if body.title is not None:
            updates["title"] = body.title
        if body.content is not None:
            updates["content"] = body.content
        if body.tags is not None:
            updates["tags"] = body.tags

        updated = storage.update_post(post_id, **updates)
        return updated.to_dict()

    @app.delete("/posts/{post_id}", response_model=MessageResponse, tags=["Posts"])
    async def delete_post(
        post_id: str,
        current_user: dict = Depends(get_current_user),
        storage: InMemoryStorage = Depends(get_storage),
        rbac=Depends(get_rbac),
    ):
        """Delete a post. Authors can delete their own; editors/admins can delete any."""
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Post not found"})

        is_owner = post.author_id == current_user["user_id"]
        role = current_user.get("role")

        # Admin and editor can delete any post; authors can only delete their own
        if role in ("admin", "editor"):
            can_delete = True
        elif role == "author" and is_owner:
            can_delete = True
        else:
            can_delete = False
        if not can_delete:
            raise HTTPException(
                status_code=403,
                detail={"error": "Forbidden", "message": "You do not have permission to delete this post"},
            )

        storage.delete_post(post_id)
        return MessageResponse(message="Post deleted successfully")

    @app.put("/posts/{post_id}/publish", tags=["Posts"])
    async def publish_post(
        post_id: str,
        current_user: dict = Depends(get_current_user),
        _perm: None = Depends(RequirePermission("publish", "post")),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Toggle a post's published/draft status."""
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Post not found"})

        new_status = PostStatus.PUBLISHED if post.status == PostStatus.DRAFT else PostStatus.DRAFT
        updated = storage.update_post(post_id, status=new_status)
        return {
            **updated.to_dict(),
            "message": f"Post {'published' if new_status == PostStatus.PUBLISHED else 'unpublished'} successfully",
        }

    # ── Comments ─────────────────────────────────────────────────────────────

    @app.get("/posts/{post_id}/comments", response_model=CommentListResponse, tags=["Comments"])
    async def get_comments(
        post_id: str,
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Get all comments for a post."""
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Post not found"})

        comments = storage.list_comments(post_id=post_id)
        return CommentListResponse(
            comments=[c.to_dict() for c in comments],
            total=len(comments),
        )

    @app.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=201, tags=["Comments"])
    async def add_comment(
        post_id: str,
        body: CreateCommentRequest,
        current_user: dict = Depends(get_current_user),
        _perm: None = Depends(RequirePermission("create", "comment")),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Add a comment to a post."""
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Post not found"})

        if post.status != PostStatus.PUBLISHED:
            raise HTTPException(
                status_code=400,
                detail={"error": "Bad Request", "message": "Cannot comment on non-published posts"},
            )

        comment = storage.create_comment(
            post_id=post_id,
            content=body.content,
            author_id=current_user["user_id"],
            author_username=current_user["username"],
        )
        return CommentResponse(**comment.to_dict())

    @app.delete("/comments/{comment_id}", response_model=MessageResponse, tags=["Comments"])
    async def delete_comment(
        comment_id: str,
        current_user: dict = Depends(get_current_user),
        storage: InMemoryStorage = Depends(get_storage),
        rbac=Depends(get_rbac),
    ):
        """Delete a comment. Authors can delete their own; editors/admins can delete any."""
        comment = storage.get_comment(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "Comment not found"})

        is_owner = comment.author_id == current_user["user_id"]
        role = current_user.get("role")

        # Admin and editor can delete any comment; anyone who owns it can delete it
        if role in ("admin", "editor"):
            can_delete = True
        elif is_owner:
            can_delete = True
        else:
            can_delete = False
        if not can_delete:
            raise HTTPException(
                status_code=403,
                detail={"error": "Forbidden", "message": "You do not have permission to delete this comment"},
            )

        storage.delete_comment(comment_id)
        return MessageResponse(message="Comment deleted successfully")

    # ── Admin ────────────────────────────────────────────────────────────────

    @app.get("/admin/users", response_model=UserListResponse, tags=["Admin"])
    async def list_users(
        current_user: dict = Depends(get_current_user),
        _role: None = Depends(RequireRole("admin")),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """List all users (admin only)."""
        users = storage.list_users()
        return UserListResponse(
            users=[
                UserResponse(
                    id=u.id, username=u.username, email=u.email,
                    role=u.role, created_at=u.created_at.isoformat(),
                )
                for u in users
            ],
            total=len(users),
        )

    @app.put("/admin/users/{user_id}/role", response_model=UserResponse, tags=["Admin"])
    async def update_user_role(
        user_id: str,
        body: UpdateRoleRequest,
        current_user: dict = Depends(get_current_user),
        _role: None = Depends(RequireRole("admin")),
        storage: InMemoryStorage = Depends(get_storage),
        rbac=Depends(get_rbac),
    ):
        """Update a user's role (admin only)."""
        if user_id == current_user["user_id"]:
            raise HTTPException(
                status_code=400,
                detail={"error": "Bad Request", "message": "You cannot change your own role"},
            )

        user = storage.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail={"error": "Not Found", "message": "User not found"})

        allowed_roles = {"reader", "author", "editor", "admin"}
        if body.role not in allowed_roles:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Bad Request",
                    "message": f"Invalid role. Must be one of: {', '.join(sorted(allowed_roles))}",
                },
            )

        updated_user = storage.update_user_role(user_id, body.role)
        rbac_user_id = f"user_{user_id}"
        old_rbac_role = f"role_{user.role}"
        new_rbac_role = f"role_{body.role}"

        try:
            rbac.revoke_role(rbac_user_id, old_rbac_role)
        except Exception:
            pass
        rbac.assign_role(rbac_user_id, new_rbac_role)

        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            role=updated_user.role,
            created_at=updated_user.created_at.isoformat(),
        )

    @app.get("/admin/stats", response_model=StatsResponse, tags=["Admin"])
    async def get_stats(
        current_user: dict = Depends(get_current_user),
        _role: None = Depends(RequireRole("admin", "editor")),
        storage: InMemoryStorage = Depends(get_storage),
    ):
        """Get system statistics (admin and editor only)."""
        stats = storage.get_stats()
        return StatsResponse(
            total_users=stats.total_users,
            total_posts=stats.total_posts,
            published_posts=stats.published_posts,
            draft_posts=stats.draft_posts,
            total_comments=stats.total_comments,
        )

    return app


# ============================================================================
# Application singleton (imported by uvicorn / test client)
# ============================================================================
app = create_app()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
