"""
In-memory storage for FastAPI Blog API.
Provides CRUD for users, posts, comments, and stats.
Mirrors the Flask test-app storage exactly.
"""
from typing import Dict, List, Optional
from datetime import datetime, timezone

from models import User, Post, Comment, PostStatus, SystemStats


class InMemoryStorage:
    """In-memory storage for blog data."""

    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self.posts: Dict[str, Post] = {}
        self.comments: Dict[str, Comment] = {}
        self._next_user_id = 1
        self._next_post_id = 1
        self._next_comment_id = 1

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def create_user(
        self, username: str, email: str, password_hash: str, role: str
    ) -> User:
        user_id = str(self._next_user_id)
        self._next_user_id += 1
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
        )
        self.users[user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def list_users(self) -> List[User]:
        return list(self.users.values())

    def update_user_role(self, user_id: str, new_role: str) -> Optional[User]:
        user = self.users.get(user_id)
        if user:
            user.role = new_role
        return user

    def delete_user(self, user_id: str) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

    # ------------------------------------------------------------------
    # Posts
    # ------------------------------------------------------------------

    def create_post(
        self,
        title: str,
        content: str,
        author_id: str,
        author_username: str,
        status: PostStatus = PostStatus.DRAFT,
        tags: Optional[List[str]] = None,
    ) -> Post:
        post_id = str(self._next_post_id)
        self._next_post_id += 1
        now = datetime.now(timezone.utc)
        post = Post(
            id=post_id,
            title=title,
            content=content,
            author_id=author_id,
            author_username=author_username,
            status=status,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            published_at=now if status == PostStatus.PUBLISHED else None,
        )
        self.posts[post_id] = post
        return post

    def get_post(self, post_id: str) -> Optional[Post]:
        return self.posts.get(post_id)

    def list_posts(
        self,
        status: Optional[PostStatus] = None,
        author_id: Optional[str] = None,
    ) -> List[Post]:
        posts = list(self.posts.values())
        if status is not None:
            posts = [p for p in posts if p.status == status]
        if author_id is not None:
            posts = [p for p in posts if p.author_id == author_id]
        return sorted(posts, key=lambda p: p.created_at, reverse=True)

    def update_post(
        self,
        post_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[PostStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[Post]:
        post = self.posts.get(post_id)
        if not post:
            return None
        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        if status is not None:
            post.status = status
            if status == PostStatus.PUBLISHED and post.published_at is None:
                post.published_at = datetime.now(timezone.utc)
        if tags is not None:
            post.tags = tags
        post.updated_at = datetime.now(timezone.utc)
        return post

    def delete_post(self, post_id: str) -> bool:
        if post_id in self.posts:
            del self.posts[post_id]
            return True
        return False

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------

    def create_comment(
        self,
        post_id: str,
        content: str,
        author_id: str,
        author_username: str,
    ) -> Optional[Comment]:
        if post_id not in self.posts:
            return None
        comment_id = str(self._next_comment_id)
        self._next_comment_id += 1
        now = datetime.now(timezone.utc)
        comment = Comment(
            id=comment_id,
            post_id=post_id,
            content=content,
            author_id=author_id,
            author_username=author_username,
            created_at=now,
            updated_at=now,
        )
        self.comments[comment_id] = comment
        return comment

    def get_comment(self, comment_id: str) -> Optional[Comment]:
        return self.comments.get(comment_id)

    def list_comments(self, post_id: str) -> List[Comment]:
        return [
            c for c in self.comments.values()
            if c.post_id == post_id and not c.is_deleted
        ]

    def delete_comment(self, comment_id: str, soft: bool = True) -> bool:
        comment = self.comments.get(comment_id)
        if not comment:
            return False
        if soft:
            comment.is_deleted = True
        else:
            del self.comments[comment_id]
        return True

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self) -> SystemStats:
        published = sum(1 for p in self.posts.values() if p.status == PostStatus.PUBLISHED)
        draft = sum(1 for p in self.posts.values() if p.status == PostStatus.DRAFT)
        return SystemStats(
            total_users=len(self.users),
            total_posts=len(self.posts),
            total_comments=sum(1 for c in self.comments.values() if not c.is_deleted),
            published_posts=published,
            draft_posts=draft,
        )
