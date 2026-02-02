# Flask Blog API - Usage Examples

Complete usage examples with curl commands. Run these commands after starting the server with `python app.py`.

## Prerequisites

```bash
# Start the server
python app.py

# Server will be available at http://localhost:5000
```

## Sample Users (Preloaded)

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| admin | admin123 | admin | All permissions |
| editor | editor123 | editor | Manage all content |
| john_author | author123 | author | Create posts, edit own posts |
| jane_author | author123 | author | Create posts, edit own posts |
| bob_reader | reader123 | reader | Read only, add comments |

---

## 1. Authentication

### Register New User

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "secret123",
    "role": "author"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "6",
    "username": "alice",
    "role": "author"
  }
}
```

### Login (Get JWT Token)

```bash
# Login as author
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_author",
    "password": "author123"
  }'
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "3",
    "username": "john_author",
    "role": "author"
  },
  "expires_in": 86400
}
```

**Save the token for subsequent requests:**
```bash
# On Linux/Mac
export TOKEN="<your_token_here>"

# On Windows PowerShell
$TOKEN="<your_token_here>"
```

### Get Current User Info

```bash
curl http://localhost:5000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## 2. Reading Posts (Public Access)

### List All Published Posts

```bash
curl http://localhost:5000/posts
```

**Response:**
```json
{
  "posts": [
    {
      "id": "1",
      "title": "Getting Started with RBAC",
      "content": "Role-Based Access Control (RBAC)...",
      "status": "published",
      "author": {
        "id": "3",
        "username": "john_author"
      },
      "created_at": "2026-02-01T10:00:00",
      "tags": ["rbac", "security", "tutorial"],
      "view_count": 0
    }
  ],
  "count": 4
}
```

### Get Specific Post

```bash
curl http://localhost:5000/posts/1
```

---

## 3. Creating Content

### Create a Blog Post

```bash
# Login first to get token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_author", "password": "author123"}' \
  | jq -r '.token' > token.txt

TOKEN=$(cat token.txt)

# Create a post
curl -X POST http://localhost:5000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Post About Python",
    "content": "Python is an amazing programming language. Here are some tips...",
    "status": "draft",
    "tags": ["python", "programming"]
  }'
```

**Response:**
```json
{
  "message": "Post created successfully",
  "post": {
    "id": "6",
    "title": "My New Post About Python",
    "content": "Python is an amazing programming language...",
    "status": "draft",
    "author": {
      "id": "3",
      "username": "john_author"
    },
    "created_at": "2026-02-03T14:30:00",
    "tags": ["python", "programming"]
  }
}
```

### Add a Comment

```bash
# Add comment as reader
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "bob_reader", "password": "reader123"}' \
  | jq -r '.token' > token_reader.txt

READER_TOKEN=$(cat token_reader.txt)

curl -X POST http://localhost:5000/posts/1/comments \
  -H "Authorization: Bearer $READER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Excellent article! Very informative."
  }'
```

---

## 4. Updating Content

### Update Own Post (Author)

```bash
# Author can update their own posts
curl -X PUT http://localhost:5000/posts/6 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated: My New Post About Python",
    "content": "Python is an amazing programming language with many features...",
    "status": "draft"
  }'
```

### Try to Update Someone Else's Post (Should Fail)

```bash
# Author trying to update another author's post
curl -X PUT http://localhost:5000/posts/4 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Trying to hack this post"
  }'
```

**Response (403 Forbidden):**
```json
{
  "error": "Forbidden",
  "message": "You can only modify your own content",
  "reason": "ownership_required"
}
```

### Update Any Post (Editor/Admin)

```bash
# Login as editor
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "editor", "password": "editor123"}' \
  | jq -r '.token' > token_editor.txt

EDITOR_TOKEN=$(cat token_editor.txt)

# Editor can update any post
curl -X PUT http://localhost:5000/posts/1 \
  -H "Authorization: Bearer $EDITOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with RBAC [Updated]",
    "content": "Role-Based Access Control (RBAC) - Updated content..."
  }'
```

---

## 5. Publishing Posts

### Publish Post (Requires publish permission)

```bash
# Authors cannot publish directly (only editors/admins)
# This will fail for author:
curl -X POST http://localhost:5000/posts/6/publish \
  -H "Authorization: Bearer $TOKEN"

# But editor can publish:
curl -X POST http://localhost:5000/posts/6/publish \
  -H "Authorization: Bearer $EDITOR_TOKEN"
```

**Editor Response:**
```json
{
  "message": "Post published successfully",
  "post": {
    "id": "6",
    "status": "published",
    "published_at": "2026-02-03T15:00:00"
  }
}
```

---

## 6. Deleting Content

### Delete Own Post

```bash
# Author can delete their own posts
curl -X DELETE http://localhost:5000/posts/6 \
  -H "Authorization: Bearer $TOKEN"
```

### Delete Own Comment

```bash
# Reader can delete their own comments
curl -X DELETE http://localhost:5000/comments/1 \
  -H "Authorization: Bearer $READER_TOKEN"
```

### Delete Any Content (Editor/Admin)

```bash
# Editor can delete any post
curl -X DELETE http://localhost:5000/posts/3 \
  -H "Authorization: Bearer $EDITOR_TOKEN"
```

---

## 7. Admin Operations

### List All Users

```bash
# Login as admin
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.token' > token_admin.txt

ADMIN_TOKEN=$(cat token_admin.txt)

# List users
curl http://localhost:5000/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Response:**
```json
{
  "users": [
    {
      "id": "1",
      "username": "admin",
      "email": "admin@blogapi.com",
      "role": "admin",
      "created_at": "2026-02-03T10:00:00"
    },
    {
      "id": "3",
      "username": "john_author",
      "email": "john@blogapi.com",
      "role": "author",
      "created_at": "2026-02-03T10:00:02"
    }
  ],
  "count": 5
}
```

### Change User Role

```bash
# Promote user to editor
curl -X PUT http://localhost:5000/admin/users/3/role \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "editor"
  }'
```

### Get System Statistics

```bash
curl http://localhost:5000/admin/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Response:**
```json
{
  "total_users": 5,
  "total_posts": 5,
  "total_comments": 7,
  "published_posts": 4,
  "draft_posts": 1,
  "users_by_role": {
    "admin": 1,
    "editor": 1,
    "author": 2,
    "reader": 1
  }
}
```

---

## 8. Error Handling Examples

### Authentication Error

```bash
# Request without token
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Test"}'
```

**Response (401):**
```json
{
  "error": "Authentication required",
  "message": "No token provided"
}
```

### Authorization Error

```bash
# Reader trying to create post (readers can only read)
curl -X POST http://localhost:5000/posts \
  -H "Authorization: Bearer $READER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Test"}'
```

**Response (403):**
```json
{
  "error": "Forbidden",
  "message": "You do not have permission to create post"
}
```

### Validation Error

```bash
# Missing required fields
curl -X POST http://localhost:5000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
```

**Response (400):**
```json
{
  "error": "Validation error",
  "message": "Title and content are required"
}
```

---

## 9. Complete Workflow Example

Here's a complete workflow demonstrating RBAC in action:

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"

echo "=== Flask Blog API - Complete Workflow ==="
echo

# 1. Register new author
echo "1. Registering new author..."
curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "sam_writer", "email": "sam@example.com", "password": "writer123", "role": "author"}' \
  | jq

# 2. Login as author
echo -e "\n2. Logging in as author..."
AUTHOR_TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "sam_writer", "password": "writer123"}' \
  | jq -r '.token')

echo "Token: ${AUTHOR_TOKEN:0:20}..."

# 3. Create a post
echo -e "\n3. Creating a blog post..."
POST_ID=$(curl -s -X POST $BASE_URL/posts \
  -H "Authorization: Bearer $AUTHOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learning Flask and RBAC",
    "content": "This is a great tutorial on building secure APIs!",
    "status": "draft",
    "tags": ["flask", "tutorial"]
  }' | jq -r '.post.id')

echo "Created post ID: $POST_ID"

# 4. Update the post
echo -e "\n4. Updating the post..."
curl -s -X PUT $BASE_URL/posts/$POST_ID \
  -H "Authorization: Bearer $AUTHOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learning Flask and RBAC [Complete Guide]",
    "content": "This is a comprehensive tutorial on building secure APIs with RBAC!"
  }' | jq

# 5. Login as editor
echo -e "\n5. Logging in as editor to publish..."
EDITOR_TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "editor", "password": "editor123"}' \
  | jq -r '.token')

# 6. Publish the post
echo -e "\n6. Publishing the post..."
curl -s -X POST $BASE_URL/posts/$POST_ID/publish \
  -H "Authorization: Bearer $EDITOR_TOKEN" \
  | jq

# 7. View published post (public)
echo -e "\n7. Viewing published post (no auth required)..."
curl -s $BASE_URL/posts/$POST_ID | jq

# 8. Add comment as reader
echo -e "\n8. Logging in as reader to add comment..."
READER_TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "bob_reader", "password": "reader123"}' \
  | jq -r '.token')

curl -s -X POST $BASE_URL/posts/$POST_ID/comments \
  -H "Authorization: Bearer $READER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Excellent guide! Thank you for sharing."}' \
  | jq

echo -e "\n=== Workflow Complete ==="
```

---

## 10. Testing with Python Requests

If you prefer Python:

```python
import requests

BASE_URL = "http://localhost:5000"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "john_author",
    "password": "author123"
})
token = response.json()["token"]

# Create post
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/posts",
    headers=headers,
    json={
        "title": "Python API Client Example",
        "content": "Using requests library to interact with the API",
        "status": "published",
        "tags": ["python", "api"]
    }
)

print(response.json())

# List posts
response = requests.get(f"{BASE_URL}/posts")
posts = response.json()["posts"]

for post in posts:
    print(f"- {post['title']} by {post['author']['username']}")
```

---

## Tips

1. **Save tokens to files** for easier testing:
   ```bash
   curl ... | jq -r '.token' > token.txt
   TOKEN=$(cat token.txt)
   ```

2. **Use jq for pretty JSON** output:
   ```bash
   curl ... | jq
   ```

3. **Check response status codes**:
   ```bash
   curl -i ...  # Include headers
   curl -w "\nStatus: %{http_code}\n" ...
   ```

4. **Test different roles** to see permission differences

5. **Monitor server logs** while testing to see authorization checks in action
