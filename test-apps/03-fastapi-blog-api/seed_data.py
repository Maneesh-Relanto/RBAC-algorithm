"""
Seed data for FastAPI Blog API.
Loads sample users, posts, and comments for testing/demo.
Identical dataset to the Flask test-app for easy comparison.
"""
from datetime import datetime, timezone
from models import PostStatus


def load_seed_data(storage, rbac, auth_manager) -> None:
    """Populate storage and RBAC with demo data."""

    print("Loading seed data...")

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    users_data = [
        {"username": "admin",       "email": "admin@blogapi.com",  "password": "admin123",  "role": "admin"},
        {"username": "editor",      "email": "editor@blogapi.com", "password": "editor123", "role": "editor"},
        {"username": "john_author", "email": "john@blogapi.com",   "password": "author123", "role": "author"},
        {"username": "jane_author", "email": "jane@blogapi.com",   "password": "author123", "role": "author"},
        {"username": "bob_reader",  "email": "bob@blogapi.com",    "password": "reader123", "role": "reader"},
    ]

    created_users: dict = {}
    for ud in users_data:
        pw_hash = auth_manager.hash_password(ud["password"])
        user = storage.create_user(
            username=ud["username"],
            email=ud["email"],
            password_hash=pw_hash,
            role=ud["role"],
        )
        created_users[ud["username"]] = user

        rbac.create_user(user_id=f"user_{user.id}", email=user.email, name=user.username)
        rbac.assign_role(f"user_{user.id}", f"role_{user.role}")
        print(f"  ✓ Created user: {user.username} ({user.role})")

    # ------------------------------------------------------------------
    # Posts
    # ------------------------------------------------------------------
    posts_data = [
        {
            "title": "Getting Started with RBAC",
            "content": "Role-Based Access Control (RBAC) is a powerful authorization model. "
                       "In this post we explore the fundamentals and key concepts including "
                       "Users, Roles, Permissions, and Resources.",
            "author": "john_author",
            "status": PostStatus.PUBLISHED,
            "tags": ["rbac", "security", "tutorial"],
        },
        {
            "title": "Building REST APIs with FastAPI",
            "content": "FastAPI is a modern, high-performance Python framework for building APIs. "
                       "It features automatic OpenAPI docs, Pydantic models, and native async support.",
            "author": "john_author",
            "status": PostStatus.PUBLISHED,
            "tags": ["fastapi", "python", "api"],
        },
        {
            "title": "Draft: Advanced RBAC Patterns",
            "content": "This draft explores attribute-based access control (ABAC), "
                       "contextual permissions, and hierarchical role designs.",
            "author": "john_author",
            "status": PostStatus.DRAFT,
            "tags": ["rbac", "abac", "advanced"],
        },
        {
            "title": "Managing Blog Content at Scale",
            "content": "As your blog grows, managing content, authors, and editorial workflows "
                       "becomes critical. Here are best practices for editorial teams.",
            "author": "jane_author",
            "status": PostStatus.PUBLISHED,
            "tags": ["content", "management"],
        },
        {
            "title": "Security Best Practices for Web APIs",
            "content": "Securing your API requires more than just authentication. "
                       "We cover authorization, rate limiting, input validation, and audit logging.",
            "author": "editor",
            "status": PostStatus.PUBLISHED,
            "tags": ["security", "api", "best-practices"],
        },
    ]

    created_posts: dict = {}
    for pd in posts_data:
        author = created_users[pd["author"]]
        post = storage.create_post(
            title=pd["title"],
            content=pd["content"],
            author_id=author.id,
            author_username=author.username,
            status=pd["status"],
            tags=pd["tags"],
        )
        created_posts[pd["title"]] = post
        print(f"  ✓ Created post: '{post.title}' by {author.username}")

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------
    comments_data = [
        {"post": "Getting Started with RBAC",    "author": "bob_reader",  "content": "Great intro to RBAC!"},
        {"post": "Getting Started with RBAC",    "author": "jane_author", "content": "Really well explained."},
        {"post": "Building REST APIs with FastAPI","author": "bob_reader", "content": "FastAPI is amazing, thanks!"},
        {"post": "Building REST APIs with FastAPI","author": "editor",     "content": "Good overview of FastAPI."},
        {"post": "Managing Blog Content at Scale","author": "john_author","content": "Very useful editorial tips."},
        {"post": "Security Best Practices for Web APIs","author": "john_author","content": "Great coverage of auth patterns."},
        {"post": "Security Best Practices for Web APIs","author": "bob_reader", "content": "Can you cover OAuth next?"},
    ]

    for cd in comments_data:
        post = created_posts.get(cd["post"])
        author = created_users[cd["author"]]
        if post:
            storage.create_comment(
                post_id=post.id,
                content=cd["content"],
                author_id=author.id,
                author_username=author.username,
            )

    stats = storage.get_stats()
    print(f"\nSeed data loaded successfully!")
    print(f"  Users: {stats.total_users}")
    print(f"  Posts: {stats.total_posts} ({stats.published_posts} published)")
    print(f"  Comments: {stats.total_comments}")
