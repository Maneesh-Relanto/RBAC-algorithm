"""
Seed data for Flask Blog API.
Loads sample users, posts, and comments for testing.
"""
from datetime import datetime, timedelta
from models import PostStatus


def load_seed_data(storage, rbac, auth_manager):
    """Load sample data into storage and RBAC."""
    
    print("Loading seed data...")
    
    # ==================== Create Users ====================
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@blogapi.com',
            'password': 'admin123',
            'role': 'admin'
        },
        {
            'username': 'editor',
            'email': 'editor@blogapi.com',
            'password': 'editor123',
            'role': 'editor'
        },
        {
            'username': 'john_author',
            'email': 'john@blogapi.com',
            'password': 'author123',
            'role': 'author'
        },
        {
            'username': 'jane_author',
            'email': 'jane@blogapi.com',
            'password': 'author123',
            'role': 'author'
        },
        {
            'username': 'bob_reader',
            'email': 'bob@blogapi.com',
            'password': 'reader123',
            'role': 'reader'
        }
    ]
    
    created_users = {}
    
    for user_data in users_data:
        password_hash = auth_manager.hash_password(user_data['password'])
        user = storage.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=password_hash,
            role=user_data['role']
        )
        created_users[user_data['username']] = user
        
        # Add to RBAC using the correct API
        rbac.create_user(
            user_id=f"user_{user.id}",
            email=user.email,
            name=user.username
        )
        rbac.assign_role(f"user_{user.id}", f"role_{user.role}")
        
        print(f"  ✓ Created user: {user.username} ({user.role})")
    
    # ==================== Create Posts ====================
    
    posts_data = [
        {
            'title': 'Getting Started with RBAC',
            'content': '''Role-Based Access Control (RBAC) is a powerful authorization model that helps you manage who can do what in your application.

In this post, we'll explore the fundamentals of RBAC and how it can simplify your security implementation.

## Key Concepts

1. **Users** - People who use your system
2. **Roles** - Groups of permissions (e.g., admin, editor, reader)
3. **Permissions** - What actions can be performed (e.g., create, read, update, delete)
4. **Resources** - What things can be acted upon (e.g., posts, comments, users)

## Benefits

- Simplified permission management
- Easier auditing and compliance
- Reduced security risks
- Better separation of concerns

Stay tuned for more tutorials!''',
            'author': 'john_author',
            'status': PostStatus.PUBLISHED,
            'tags': ['rbac', 'security', 'tutorial']
        },
        {
            'title': 'Building REST APIs with Flask',
            'content': '''Flask is a lightweight and flexible Python web framework that makes it easy to build REST APIs.

In this tutorial, we'll cover the basics of creating a RESTful API with Flask, including routing, request handling, and JSON responses.

## Why Flask?

- Simple and intuitive
- Minimal boilerplate
- Great documentation
- Large ecosystem of extensions

## Basic Example

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True)
```

More examples coming soon!''',
            'author': 'john_author',
            'status': PostStatus.PUBLISHED,
            'tags': ['flask', 'python', 'api', 'tutorial']
        },
        {
            'title': 'Draft: Advanced RBAC Patterns',
            'content': '''This is a draft post about advanced RBAC patterns including:

- Hierarchical roles
- Attribute-based access control (ABAC)
- Dynamic permissions
- Context-aware authorization

Still working on this...''',
            'author': 'john_author',
            'status': PostStatus.DRAFT,
            'tags': ['rbac', 'advanced']
        },
        {
            'title': 'Managing Blog Content at Scale',
            'content': '''As your blog grows, managing content becomes more challenging. Here are some tips:

## Content Organization

1. Use tags and categories effectively
2. Implement search functionality
3. Create content calendars
4. Use editorial workflows

## Technical Considerations

- Database indexing for performance
- Caching strategies
- CDN for images and assets
- SEO optimization

## Team Collaboration

- Define clear roles (admin, editor, author)
- Use RBAC for access control
- Implement content approval workflows
- Track changes and revisions

This API demonstrates these concepts!''',
            'author': 'jane_author',
            'status': PostStatus.PUBLISHED,
            'tags': ['blogging', 'content-management', 'best-practices']
        },
        {
            'title': 'Security Best Practices for Web APIs',
            'content': '''Security should be a top priority when building web APIs. Here are essential practices:

## Authentication

- Use JWT tokens or OAuth2
- Implement token expiration
- Secure password storage (bcrypt, argon2)

## Authorization

- Implement RBAC or ABAC
- Follow principle of least privilege
- Validate all inputs

## Data Protection

- Use HTTPS in production
- Encrypt sensitive data
- Implement rate limiting
- Log security events

## Common Vulnerabilities

- SQL injection
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Insecure deserialization

Always keep security in mind!''',
            'author': 'editor',
            'status': PostStatus.PUBLISHED,
            'tags': ['security', 'api', 'best-practices']
        }
    ]
    
    created_posts = []
    
    for post_data in posts_data:
        author = created_users[post_data['author']]
        post = storage.create_post(
            title=post_data['title'],
            content=post_data['content'],
            author_id=author.id,
            author_username=author.username,
            status=post_data['status'],
            tags=post_data['tags']
        )
        created_posts.append(post)
        
        # Adjust created_at for variety
        if post.status == PostStatus.PUBLISHED:
            days_ago = len(created_posts)
            post.created_at = datetime.utcnow() - timedelta(days=days_ago)
            post.published_at = post.created_at
        
        print(f"  ✓ Created post: '{post.title}' by {author.username}")
    
    # ==================== Create Comments ====================
    
    comments_data = [
        {
            'post_index': 0,  # First post
            'author': 'bob_reader',
            'content': 'Great introduction to RBAC! Really helpful for understanding the basics.'
        },
        {
            'post_index': 0,
            'author': 'jane_author',
            'content': 'Nice article! Looking forward to the advanced patterns post.'
        },
        {
            'post_index': 1,
            'author': 'bob_reader',
            'content': 'Flask is amazing! This tutorial helped me get started quickly.'
        },
        {
            'post_index': 1,
            'author': 'editor',
            'content': 'Well written. You might want to add a section on error handling.'
        },
        {
            'post_index': 3,
            'author': 'john_author',
            'content': 'Excellent tips on content management. We should collaborate on a post about workflows!'
        },
        {
            'post_index': 4,
            'author': 'john_author',
            'content': 'Security is so important. Great coverage of the key topics.'
        },
        {
            'post_index': 4,
            'author': 'bob_reader',
            'content': 'This is a must-read for anyone building APIs. Bookmarked!'
        }
    ]
    
    for comment_data in comments_data:
        post = created_posts[comment_data['post_index']]
        author = created_users[comment_data['author']]
        
        comment = storage.create_comment(
            post_id=post.id,
            content=comment_data['content'],
            author_id=author.id,
            author_username=author.username
        )
        
        if comment:
            print(f"  ✓ Created comment by {author.username} on '{post.title}'")
    
    print(f"\nSeed data loaded successfully!")
    print(f"  Users: {len(created_users)}")
    print(f"  Posts: {len(created_posts)} ({len([p for p in created_posts if p.status == PostStatus.PUBLISHED])} published)")
    print(f"  Comments: {len(comments_data)}")
    print()
