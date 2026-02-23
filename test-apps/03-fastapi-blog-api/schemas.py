"""
Pydantic schemas for FastAPI Blog API request and response validation.
FastAPI uses these for automatic OpenAPI docs and JSON validation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, field_validator

from models import PostStatus

# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "reader"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid = {"admin", "editor", "author", "reader"}
        if v.lower() not in valid:
            raise ValueError(f"Role must be one of: {', '.join(sorted(valid))}")
        return v.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError("Password cannot be empty")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return v.strip()


class UserPublicResponse(BaseModel):
    id: str
    username: str
    role: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    message: Optional[str] = None


# ---------------------------------------------------------------------------
# Post schemas
# ---------------------------------------------------------------------------

class CreatePostRequest(BaseModel):
    title: str
    content: str
    status: str = "draft"
    tags: List[str] = []

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Content cannot be empty")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        try:
            PostStatus(v.lower())
        except ValueError:
            valid = [s.value for s in PostStatus]
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid)}")
        return v.lower()


class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            PostStatus(v.lower())
        except ValueError:
            valid = [s.value for s in PostStatus]
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid)}")
        return v.lower()


class AuthorSummary(BaseModel):
    id: str
    username: str


class PostSummaryResponse(BaseModel):
    id: str
    title: str
    content: str
    status: str
    author: AuthorSummary
    created_at: str
    updated_at: str
    tags: List[str]
    view_count: int


class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    status: str
    author: AuthorSummary
    created_at: str
    updated_at: str
    published_at: Optional[str]
    tags: List[str]
    view_count: int


class PostListResponse(BaseModel):
    posts: List[PostSummaryResponse]
    total: int
    count: Optional[int] = None  # alias for backwards compat


# ---------------------------------------------------------------------------
# Comment schemas
# ---------------------------------------------------------------------------

class CreateCommentRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Content cannot be empty")
        return v


class CommentResponse(BaseModel):
    id: str
    post_id: str
    content: str
    author: AuthorSummary
    created_at: str
    updated_at: str


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    count: Optional[int] = None


# ---------------------------------------------------------------------------
# Admin schemas
# ---------------------------------------------------------------------------

class UpdateRoleRequest(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid = {"admin", "editor", "author", "reader"}
        if v.lower() not in valid:
            raise ValueError(f"Role must be one of: {', '.join(sorted(valid))}")
        return v.lower()


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    count: Optional[int] = None


class StatsResponse(BaseModel):
    total_users: int
    total_posts: int
    total_comments: int
    published_posts: int
    draft_posts: int


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    detail: Optional[Any] = None


class HealthResponse(BaseModel):
    status: str
    service: Optional[str] = None
    version: Optional[str] = None
    timestamp: Optional[str] = None
