"""
Data models for Flask Blog API.
Simple dataclass-based models for posts, comments, and users.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PostStatus(str, Enum):
    """Post status enumeration."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'


@dataclass
class User:
    """User model."""
    id: str
    username: str
    email: str
    password_hash: str
    role: str  # admin, editor, author, reader
    created_at: datetime = field(default_factory=_utcnow)
    
    def to_dict(self, include_password: bool = False) -> dict:
        """Convert user to dictionary (excluding password by default)."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data
    
    def to_public_dict(self) -> dict:
        """Convert user to public dictionary (minimal info)."""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }


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
        """Convert post to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status.value if isinstance(self.status, PostStatus) else self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'tags': self.tags,
            'view_count': self.view_count
        }
        
        if include_author:
            data['author'] = {
                'id': self.author_id,
                'username': self.author_username
            }
        
        return data
    
    def to_summary_dict(self) -> dict:
        """Convert post to summary dictionary (for list views)."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'status': self.status.value if isinstance(self.status, PostStatus) else self.status,
            'author': {
                'id': self.author_id,
                'username': self.author_username
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags,
            'view_count': self.view_count
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
        """Convert comment to dictionary."""
        data = {
            'id': self.id,
            'post_id': self.post_id,
            'content': self.content if not self.is_deleted else '[deleted]',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_deleted': self.is_deleted
        }
        
        if include_author and not self.is_deleted:
            data['author'] = {
                'id': self.author_id,
                'username': self.author_username
            }
        
        return data


@dataclass
class AuthToken:
    """Authentication token model."""
    token: str
    user_id: str
    username: str
    role: str
    expires_at: datetime
    
    def to_dict(self) -> dict:
        """Convert token to dictionary."""
        return {
            'token': self.token,
            'user': {
                'id': self.user_id,
                'username': self.username,
                'role': self.role
            },
            'expires_at': self.expires_at.isoformat()
        }


@dataclass
class SystemStats:
    """System statistics model."""
    total_users: int
    total_posts: int
    total_comments: int
    published_posts: int
    draft_posts: int
    users_by_role: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert stats to dictionary."""
        return {
            'total_users': self.total_users,
            'total_posts': self.total_posts,
            'total_comments': self.total_comments,
            'published_posts': self.published_posts,
            'draft_posts': self.draft_posts,
            'users_by_role': self.users_by_role
        }
