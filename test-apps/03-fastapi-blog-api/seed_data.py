"""
Seed data for FastAPI Blog API.
Loads sample users, posts, and comments for testing/demo.
Identical dataset to the Flask test-app for easy comparison.
"""
from datetime import datetime, timezone
from models import PostStatus

# ---------------------------------------------------------------------------
# Post-title constants (reused across seeding and comment linking)
# ---------------------------------------------------------------------------
TITLE_RBAC_INTRO = "Getting Started with RBAC"
TITLE_FASTAPI_REST = "Building REST APIs with FastAPI"
TITLE_SECURITY = "Security Best Practices for Web APIs"


def load_seed_data(storage, rbac, auth_manager) -> None:
    """Populate storage and RBAC with demo data."""

    print("Loading seed data...")

    # ------------------------------------------------------------------
    # Users  (passwords are intentional demo-only values)
    # ------------------------------------------------------------------
    users_data = [
        {"username": "admin",       "email": "admin@blogapi.com",  "password": "admin123",  "role": "admin"},   # NOSONAR
        {"username": "editor",      "email": "editor@blogapi.com", "password": "editor123", "role": "editor"},  # NOSONAR
        {"username": "john_author", "email": "john@blogapi.com",   "password": "author123", "role": "author"},  # NOSONAR
        {"username": "jane_author", "email": "jane@blogapi.com",   "password": "author123", "role": "author"},  # NOSONAR
        {"username": "bob_reader",  "email": "bob@blogapi.com",    "password": "reader123", "role": "reader"},  # NOSONAR
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
            "title": TITLE_RBAC_INTRO,
            "content": "Role-Based Access Control (RBAC) is a powerful authorization model. "
                       "In this post we explore the fundamentals and key concepts including "
                       "Users, Roles, Permissions, and Resources.",
            "author": "john_author",
            "status": PostStatus.PUBLISHED,
            "tags": ["rbac", "security", "tutorial"],
        },
        {
            "title": TITLE_FASTAPI_REST,
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
            "title": TITLE_SECURITY,
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
        {"post": TITLE_RBAC_INTRO,     "author": "bob_reader",  "content": "Great intro to RBAC!"},
        {"post": TITLE_RBAC_INTRO,     "author": "jane_author", "content": "Really well explained."},
        {"post": TITLE_FASTAPI_REST,   "author": "bob_reader",  "content": "FastAPI is amazing, thanks!"},
        {"post": TITLE_FASTAPI_REST,   "author": "editor",      "content": "Good overview of FastAPI."},
        {"post": "Managing Blog Content at Scale","author": "john_author","content": "Very useful editorial tips."},
        {"post": TITLE_SECURITY,       "author": "john_author", "content": "Great coverage of auth patterns."},
        {"post": TITLE_SECURITY,       "author": "bob_reader",  "content": "Can you cover OAuth next?"},
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
    print("\nSeed data loaded successfully!")
    print(f"  Users: {stats.total_users}")
    print(f"  Posts: {stats.total_posts} ({stats.published_posts} published)")
    print(f"  Comments: {stats.total_comments}")
