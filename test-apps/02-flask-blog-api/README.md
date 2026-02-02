# Flask Blog API - RBAC Test Application

A complete REST API demonstrating RBAC Algorithm integration with Flask, featuring JWT authentication, blog post management, and role-based authorization.

## 🎯 Purpose

This test application validates the RBAC Algorithm library in a real-world Flask REST API scenario, demonstrating:

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control** - Admin, Editor, Author, Reader roles
- **Attribute-Based Permissions** - Context-aware authorization (own posts)
- **RESTful API Design** - Complete CRUD operations
- **Decorator Pattern** - `@require_permission` decorators
- **Multi-tenant Ready** - Domain isolation support

## 🏗️ Architecture

```
┌─────────────────┐
│  Flask Routes   │ ← JWT Auth + RBAC Decorators
├─────────────────┤
│ Business Logic  │ ← Blog, Comment operations
├─────────────────┤
│  RBAC Engine    │ ← Authorization checks
├─────────────────┤
│ In-Memory Store │ ← Users, Posts, Comments
└─────────────────┘
```

## 📋 Features

### **Roles & Permissions**

| Role | Permissions |
|------|-------------|
| **Admin** | All permissions, can manage users and all content |
| **Editor** | Create, read, update, delete any post/comment |
| **Author** | Create posts, read all, update/delete own posts |
| **Reader** | Read posts and comments only |

### **Endpoints**

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

#### Blog Posts
- `GET /posts` - List all posts (public)
- `GET /posts/<id>` - Get post details (public)
- `POST /posts` - Create post (requires: `create:post`)
- `PUT /posts/<id>` - Update post (requires: `update:post` + ownership)
- `DELETE /posts/<id>` - Delete post (requires: `delete:post` + ownership)
- `POST /posts/<id>/publish` - Publish post (requires: `publish:post`)

#### Comments
- `GET /posts/<id>/comments` - List comments (public)
- `POST /posts/<id>/comments` - Add comment (requires: `create:comment`)
- `DELETE /comments/<id>` - Delete comment (requires: `delete:comment` + ownership)

#### Admin
- `GET /admin/users` - List all users (admin only)
- `PUT /admin/users/<id>/role` - Change user role (admin only)
- `GET /admin/stats` - Get system statistics (admin only)

## 🚀 Quick Start

### Prerequisites

```bash
# Ensure RBAC library is installed
cd "c:\Users\Maneesh Thakur\Downloads\My Projects\RBAC algorithm"
pip install -e .
```

### Installation

```bash
# Navigate to this directory
cd test-apps/02-flask-blog-api

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The API will start at `http://localhost:5000`

## 📚 Usage Examples

### 1. Register & Login

```bash
# Register as an author
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "secret123", "role": "author"}'

# Login to get JWT token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "secret123"}'

# Response: {"token": "eyJ0eXAiOiJKV1QiLCJhbGc..."}
```

### 2. Create a Blog Post

```bash
# Create a post (requires authentication)
curl -X POST http://localhost:5000/posts \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "content": "This is my first blog post!",
    "status": "draft"
  }'
```

### 3. Read Posts (Public)

```bash
# List all posts (no auth needed)
curl http://localhost:5000/posts

# Get specific post
curl http://localhost:5000/posts/1
```

### 4. Update Own Post

```bash
# Update your own post (requires ownership)
curl -X PUT http://localhost:5000/posts/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content"
  }'
```

### 5. Add Comments

```bash
# Add a comment
curl -X POST http://localhost:5000/posts/1/comments \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post!"
  }'
```

### 6. Admin Operations

```bash
# List all users (admin only)
curl http://localhost:5000/admin/users \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# Change user role (admin only)
curl -X PUT http://localhost:5000/admin/users/2/role \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role": "editor"}'
```

See [EXAMPLES.md](EXAMPLES.md) for complete curl examples with real tokens.

## 🧪 Testing

```bash
# Run all tests
pytest test_api.py -v

# Run with coverage
pytest test_api.py --cov=. --cov-report=html

# Test specific scenarios
pytest test_api.py -k "test_post_creation"
```

## 🔐 Security Features

1. **JWT Authentication** - Secure token-based auth with expiration
2. **Password Hashing** - Bcrypt for secure password storage
3. **Role Validation** - RBAC enforces permissions on all endpoints
4. **Ownership Checks** - Users can only modify their own content (ABAC)
5. **Input Validation** - All inputs validated and sanitized
6. **Error Handling** - Secure error messages, no sensitive data leaks

## 📁 Project Structure

```
02-flask-blog-api/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── auth.py                # JWT authentication logic
├── decorators.py          # RBAC decorators (@require_permission)
├── models.py              # Data models (Post, Comment, User)
├── storage.py             # In-memory data storage
├── seed_data.py           # Sample data for testing
├── test_api.py            # Comprehensive API tests
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── EXAMPLES.md            # Detailed usage examples
```

## 🎓 What You'll Learn

1. **Flask Integration** - How to integrate RBAC with Flask apps
2. **JWT Auth** - Implementing secure token-based authentication
3. **Decorators** - Creating reusable RBAC decorators
4. **ABAC** - Using attributes (ownership) for fine-grained control
5. **REST API Design** - Building secure, well-structured APIs
6. **Testing** - Comprehensive API testing strategies

## 🔄 Comparison with Other Test Apps

| Feature | 00-simple-cli | 01-streamlit-ui | 02-flask-blog-api |
|---------|---------------|-----------------|-------------------|
| Interface | CLI | Web UI | REST API |
| Auth | None | Simple | JWT |
| Complexity | Low | Medium | High |
| Use Case | Learning | Demo | Production-like |
| API | Direct | Direct | HTTP |

## 🚧 Limitations

- **In-Memory Storage** - Data lost on restart (use for demo only)
- **Single Instance** - Not designed for horizontal scaling
- **No Database** - Real apps should use PostgreSQL/MySQL
- **Basic Auth** - Production should add OAuth2, 2FA, etc.

## 🔮 Next Steps

After understanding this example:

1. Replace in-memory storage with SQLite/PostgreSQL adapter
2. Add pagination and filtering to list endpoints
3. Implement rate limiting and request throttling
4. Add comprehensive logging and monitoring
5. Deploy to production with gunicorn + nginx

## 📖 Related Resources

- [RBAC Algorithm Documentation](../../docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [JWT.io](https://jwt.io/) - JWT debugger and docs
- [REST API Best Practices](https://restfulapi.net/)

## 📝 License

MIT License - Same as parent RBAC Algorithm project

---

**Created**: February 3, 2026  
**Status**: ✅ Complete & Tested  
**Maintainer**: RBAC Algorithm Team
