"""
Data models for FastAPI Blog API.
Simple dataclass-based models for posts, comments, and users.
Mirrors the Flask test-app models for consistency.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum


class PostStatus(str, Enum):
    """Post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class User:
    """User model."""
    id: str
    username: str
    email: str
    password_hash: str
    role: str          # admin | editor | author | reader
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self, include_password: bool = False) -> dict:
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data

    def to_public_dict(self) -> dict:
        return {"id": self.id, "username": self.username, "role": self.role}


@dataclass
class Post:
    """Blog post model."""
    id: str
    title: str
    content: str
    author_id: str
    author_username: str
    status: PostStatus = PostStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    view_count: int = 0

    def to_dict(self, include_author: bool = True) -> dict:
        data = {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "status": self.status.value if isinstance(self.status, PostStatus) else self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "tags": self.tags,
            "view_count": self.view_count,
        }
        if include_author:
            data["author"] = {"id": self.author_id, "username": self.author_username}
        return data

    def to_summary_dict(self) -> dict:
        preview = self.content[:200] + "..." if len(self.content) > 200 else self.content
        return {
            "id": self.id,
            "title": self.title,
            "content": preview,
            "status": self.status.value if isinstance(self.status, PostStatus) else self.status,
            "author": {"id": self.author_id, "username": self.author_username},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "view_count": self.view_count,
        }


@dataclass
class Comment:
    """Comment model."""
    id: str
    post_id: str
    content: str
    author_id: str
    author_username: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = False

    def to_dict(self, include_author: bool = True) -> dict:
        data = {
            "id": self.id,
            "post_id": self.post_id,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_author:
            data["author"] = {"id": self.author_id, "username": self.author_username}
        return data


@dataclass
class SystemStats:
    """System statistics model."""
    total_users: int = 0
    total_posts: int = 0
    total_comments: int = 0
    published_posts: int = 0
    draft_posts: int = 0

    def to_dict(self) -> dict:
        return {
            "total_users": self.total_users,
            "total_posts": self.total_posts,
            "total_comments": self.total_comments,
            "published_posts": self.published_posts,
            "draft_posts": self.draft_posts,
        }
