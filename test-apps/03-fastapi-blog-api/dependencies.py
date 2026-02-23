"""
RBAC Dependency Injection for FastAPI Blog API.

Replaces Flask's custom decorators with FastAPI's native DI system.
Each class/function is a callable that can be used with Depends().

Usage in routes::

    @router.post("/posts")
    def create_post(
        data: CreatePostRequest,
        current_user: dict = Depends(get_current_user),
        _rbac: None = Depends(RequirePermission("create", "post")),
        storage: InMemoryStorage = Depends(get_storage),
        rbac: RBAC = Depends(get_rbac),
    ): ...
"""
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from auth import get_current_user
from storage import InMemoryStorage

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# App-state accessors (thin DI wrappers over request.app.state)
# ---------------------------------------------------------------------------

def get_storage(request: Request) -> InMemoryStorage:
    """Return the shared InMemoryStorage from app.state."""
    return request.app.state.storage


def get_rbac(request: Request):
    """Return the shared RBAC instance from app.state."""
    return request.app.state.rbac


# ---------------------------------------------------------------------------
# Permission dependency (class-based, works with Depends)
# ---------------------------------------------------------------------------

class RequirePermission:
    """
    FastAPI dependency that enforces an RBAC permission check.

    Optionally verifies resource ownership when *check_ownership* is True.
    The resource ID is read from path parameters (``post_id`` or ``comment_id``).

    Example::

        @router.put("/posts/{post_id}")
        def update_post(
            post_id: int,
            data: UpdatePostRequest,
            current_user: dict = Depends(get_current_user),
            _: None = Depends(RequirePermission("update", "post", check_ownership=True)),
        ): ...
    """

    def __init__(
        self,
        action: str,
        resource_type: Optional[str] = None,
        check_ownership: bool = False,
    ) -> None:
        self.action = action
        self.resource_type = resource_type
        self.check_ownership = check_ownership

    def __call__(
        self,
        request: Request,
        current_user: dict = Depends(get_current_user),
        storage: InMemoryStorage = Depends(get_storage),
        rbac=Depends(get_rbac),
    ) -> None:
        """Perform the RBAC check; raises HTTPException on failure."""
        resource = None

        if self.check_ownership:
            resource_id = (
                request.path_params.get("post_id")
                or request.path_params.get("comment_id")
                or request.path_params.get("id")
            )
            if resource_id:
                resource_id = str(resource_id)
                if self.resource_type and "post" in self.resource_type:
                    resource = storage.get_post(resource_id)
                elif self.resource_type and "comment" in self.resource_type:
                    resource = storage.get_comment(resource_id)

                if resource is None:
                    label = (self.resource_type or "resource").capitalize()
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={"error": "Not found", "message": f"{label} not found"},
                    )

        try:
            context: dict = {
                "user_id": current_user["user_id"],
                "username": current_user["username"],
                "role": current_user["role"],
            }

            if resource is not None:
                owner_id = getattr(resource, "author_id", None) or getattr(resource, "user_id", None)
                context["resource_owner"] = owner_id
                context["is_owner"] = owner_id == current_user["user_id"]

            rbac_user_id = f"user_{current_user['user_id']}"
            can_access = rbac.can(
                user_id=rbac_user_id,
                action=self.action,
                resource=self.resource_type,
                context=context,
            )

            if not can_access:
                if self.check_ownership and resource and not context.get("is_owner"):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "error": "Forbidden",
                            "message": "You can only modify your own content",
                            "reason": "ownership_required",
                        },
                    )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Forbidden",
                        "message": f"You do not have permission to {self.action} {self.resource_type}",
                        "reason": "permission_denied",
                    },
                )

        except HTTPException:
            raise  # Re-raise HTTP exceptions untouched
        except Exception as exc:
            logger.error("Authorization check failed: %s", str(exc), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Authorization error", "message": "Failed to check permissions"},
            )


# ---------------------------------------------------------------------------
# Role dependency
# ---------------------------------------------------------------------------

class RequireRole:
    """
    FastAPI dependency that enforces one of the specified role(s).

    Example::

        @router.get("/admin/users")
        def list_users(
            current_user: dict = Depends(get_current_user),
            _: None = Depends(RequireRole("admin")),
        ): ...
    """

    def __init__(self, *roles: str) -> None:
        self.roles = roles

    def __call__(self, current_user: dict = Depends(get_current_user)) -> None:
        if current_user.get("role") not in self.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Forbidden",
                    "message": f"This action requires one of these roles: {', '.join(self.roles)}",
                    "your_role": current_user.get("role"),
                },
            )


# Shorthand singleton for admin-only routes
require_admin = RequireRole("admin")
