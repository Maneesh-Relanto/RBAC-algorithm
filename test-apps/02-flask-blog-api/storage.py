"""
In-memory storage for Flask Blog API.
Provides simple CRUD operations for users, posts, and comments.
"""
from typing import List, Optional, Dict
from datetime import datetime
from models import User, Post, Comment, PostStatus, SystemStats


class InMemoryStorage:
    """In-memory storage for blog data."""
    
    def __init__(self):
        """Initialize empty storage."""
        self.users: Dict[str, User] = {}
        self.posts: Dict[str, Post] = {}
        self.comments: Dict[str, Comment] = {}
        self._next_user_id = 1
        self._next_post_id = 1
        self._next_comment_id = 1
    
    # ==================== User Operations ====================
    
    def create_user(self, username: str, email: str, password_hash: str, role: str) -> User:
        """Create a new user."""
        user_id = str(self._next_user_id)
        self._next_user_id += 1
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def list_users(self) -> List[User]:
        """List all users."""
        return list(self.users.values())
    
    def update_user_role(self, user_id: str, new_role: str) -> Optional[User]:
        """Update user's role."""
        user = self.users.get(user_id)
        if user:
            user.role = new_role
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    # ==================== Post Operations ====================
    
    def create_post(self, title: str, content: str, author_id: str, 
                   author_username: str, status: PostStatus = PostStatus.DRAFT,
                   tags: List[str] = None) -> Post:
        """Create a new post."""
        post_id = str(self._next_post_id)
        self._next_post_id += 1
        
        post = Post(
            id=post_id,
            title=title,
            content=content,
            author_id=author_id,
            author_username=author_username,
            status=status,
            tags=tags or []
        )
        
        if status == PostStatus.PUBLISHED:
            post.published_at = datetime.utcnow()
        
        self.posts[post_id] = post
        return post
    
    def get_post(self, post_id: str) -> Optional[Post]:
        """Get post by ID."""
        post = self.posts.get(post_id)
        if post:
            # Increment view count
            post.view_count += 1
        return post
    
    def list_posts(self, status: Optional[PostStatus] = None, 
                  author_id: Optional[str] = None) -> List[Post]:
        """List posts with optional filters."""
        posts = list(self.posts.values())
        
        if status:
            posts = [p for p in posts if p.status == status]
        
        if author_id:
            posts = [p for p in posts if p.author_id == author_id]
        
        # Sort by created_at descending (newest first)
        posts.sort(key=lambda p: p.created_at, reverse=True)
        
        return posts
    
    def update_post(self, post_id: str, title: Optional[str] = None,
                   content: Optional[str] = None, status: Optional[PostStatus] = None,
                   tags: Optional[List[str]] = None) -> Optional[Post]:
        """Update a post."""
        post = self.posts.get(post_id)
        if not post:
            return None
        
        if title is not None:
            post.title = title
        
        if content is not None:
            post.content = content
        
        if status is not None:
            old_status = post.status
            post.status = status
            # Set published_at when transitioning to published
            if status == PostStatus.PUBLISHED and old_status != PostStatus.PUBLISHED:
                post.published_at = datetime.utcnow()
        
        if tags is not None:
            post.tags = tags
        
        post.updated_at = datetime.utcnow()
        
        return post
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post and its comments."""
        if post_id in self.posts:
            # Delete associated comments
            comment_ids = [cid for cid, c in self.comments.items() if c.post_id == post_id]
            for cid in comment_ids:
                del self.comments[cid]
            
            # Delete post
            del self.posts[post_id]
            return True
        return False
    
    def get_posts_by_author(self, author_id: str) -> List[Post]:
        """Get all posts by a specific author."""
        return [p for p in self.posts.values() if p.author_id == author_id]
    
    # ==================== Comment Operations ====================
    
    def create_comment(self, post_id: str, content: str, 
                      author_id: str, author_username: str) -> Optional[Comment]:
        """Create a new comment."""
        # Check if post exists
        if post_id not in self.posts:
            return None
        
        comment_id = str(self._next_comment_id)
        self._next_comment_id += 1
        
        comment = Comment(
            id=comment_id,
            post_id=post_id,
            content=content,
            author_id=author_id,
            author_username=author_username
        )
        
        self.comments[comment_id] = comment
        return comment
    
    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID."""
        return self.comments.get(comment_id)
    
    def list_comments(self, post_id: Optional[str] = None) -> List[Comment]:
        """List comments, optionally filtered by post."""
        comments = list(self.comments.values())
        
        if post_id:
            comments = [c for c in comments if c.post_id == post_id]
        
        # Sort by created_at ascending (oldest first)
        comments.sort(key=lambda c: c.created_at)
        
        return comments
    
    def update_comment(self, comment_id: str, content: str) -> Optional[Comment]:
        """Update a comment."""
        comment = self.comments.get(comment_id)
        if not comment:
            return None
        
        comment.content = content
        comment.updated_at = datetime.utcnow()
        
        return comment
    
    def delete_comment(self, comment_id: str, soft: bool = True) -> bool:
        """
        Delete a comment.
        
        Args:
            comment_id: Comment ID
            soft: If True, mark as deleted. If False, remove completely.
        """
        comment = self.comments.get(comment_id)
        if not comment:
            return False
        
        if soft:
            comment.is_deleted = True
            comment.content = '[deleted]'
            comment.updated_at = datetime.utcnow()
        else:
            del self.comments[comment_id]
        
        return True
    
    # ==================== Statistics ====================
    
    def get_stats(self) -> SystemStats:
        """Get system statistics."""
        users_by_role = {}
        for user in self.users.values():
            users_by_role[user.role] = users_by_role.get(user.role, 0) + 1
        
        published_posts = len([p for p in self.posts.values() if p.status == PostStatus.PUBLISHED])
        draft_posts = len([p for p in self.posts.values() if p.status == PostStatus.DRAFT])
        
        return SystemStats(
            total_users=len(self.users),
            total_posts=len(self.posts),
            total_comments=len(self.comments),
            published_posts=published_posts,
            draft_posts=draft_posts,
            users_by_role=users_by_role
        )
    
    # ==================== Utility Methods ====================
    
    def clear_all(self):
        """Clear all data (useful for testing)."""
        self.users.clear()
        self.posts.clear()
        self.comments.clear()
        self._next_user_id = 1
        self._next_post_id = 1
        self._next_comment_id = 1
