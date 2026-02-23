"""
Comprehensive tests for Flask Blog API.
Tests authentication, authorization, CRUD operations, and RBAC.
"""
import pytest
import json
from datetime import datetime
from app import create_app
from models import PostStatus


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def tokens(client):
    """Get auth tokens for all test users."""
    users = {
        'admin': {'username': 'admin', 'password': 'admin123'},
        'editor': {'username': 'editor', 'password': 'editor123'},
        'author': {'username': 'john_author', 'password': 'author123'},
        'reader': {'username': 'bob_reader', 'password': 'reader123'}
    }
    
    tokens = {}
    for role, credentials in users.items():
        response = client.post('/auth/login', json=credentials)
        assert response.status_code == 200
        tokens[role] = response.json['token']
    
    return tokens


def get_auth_header(token):
    """Helper to create authorization header."""
    return {'Authorization': f'Bearer {token}'}


# ==================== Health & Info Tests ====================

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_index(client):
    """Test index endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.json
    assert 'name' in data
    assert 'endpoints' in data


# ==================== Authentication Tests ====================

def test_register_success(client):
    """Test successful user registration."""
    response = client.post('/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'role': 'author'
    })
    assert response.status_code == 201
    data = response.json
    assert data['message'] == 'User registered successfully'
    assert data['user']['username'] == 'newuser'
    assert data['user']['role'] == 'author'


def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    response = client.post('/auth/register', json={
        'username': 'admin',
        'email': 'another@example.com',
        'password': 'password123',
        'role': 'reader'
    })
    assert response.status_code == 409
    assert 'already exists' in response.json['message']


def test_register_invalid_role(client):
    """Test registration with invalid role."""
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'role': 'invalid_role'
    })
    assert response.status_code == 400


def test_login_success(client):
    """Test successful login."""
    response = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 200
    data = response.json
    assert 'token' in data
    assert data['user']['username'] == 'admin'


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401


def test_get_current_user(client, tokens):
    """Test getting current user info."""
    response = client.get('/auth/me', headers=get_auth_header(tokens['author']))
    assert response.status_code == 200
    data = response.json
    assert data['username'] == 'john_author'
    assert data['role'] == 'author'


# ==================== Post CRUD Tests ====================

def test_list_posts_anonymous(client):
    """Test listing posts without authentication."""
    response = client.get('/posts')
    assert response.status_code == 200
    data = response.json
    assert 'posts' in data
    assert data['count'] >= 0
    # Should only see published posts
    for post in data['posts']:
        assert post['status'] == 'published'


def test_list_posts_authenticated(client, tokens):
    """Test listing posts with authentication."""
    response = client.get('/posts', headers=get_auth_header(tokens['author']))
    assert response.status_code == 200
    # Authenticated users can see their own drafts + published posts


def test_get_post_published(client):
    """Test getting a published post without auth."""
    response = client.get('/posts/1')
    assert response.status_code == 200
    data = response.json
    assert 'title' in data
    assert 'content' in data


def test_create_post_as_author(client, tokens):
    """Test creating a post as author."""
    response = client.post('/posts',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'Test Post',
            'content': 'This is a test post content',
            'status': 'draft',
            'tags': ['test']
        }
    )
    assert response.status_code == 201
    data = response.json
    assert data['message'] == 'Post created successfully'
    assert data['post']['title'] == 'Test Post'
    assert data['post']['status'] == 'draft'


def test_create_post_as_reader_fails(client, tokens):
    """Test that reader cannot create posts."""
    response = client.post('/posts',
        headers=get_auth_header(tokens['reader']),
        json={
            'title': 'Test Post',
            'content': 'This should fail',
            'status': 'draft'
        }
    )
    assert response.status_code == 403


def test_create_post_without_auth_fails(client):
    """Test creating post without authentication."""
    response = client.post('/posts', json={
        'title': 'Test Post',
        'content': 'This should fail'
    })
    assert response.status_code == 401


def test_update_own_post(client, tokens):
    """Test updating own post as author."""
    # First create a post
    create_response = client.post('/posts',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'Original Title',
            'content': 'Original content',
            'status': 'draft'
        }
    )
    post_id = create_response.json['post']['id']
    
    # Update it
    response = client.put(f'/posts/{post_id}',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'Updated Title',
            'content': 'Updated content'
        }
    )
    assert response.status_code == 200
    data = response.json
    assert data['post']['title'] == 'Updated Title'


def test_update_others_post_as_author_fails(client, tokens):
    """Test that author cannot update another author's posts."""
    # Post 4 is created by jane_author in seed data; john_author (tokens['author'])
    # does not own it, so this should be rejected.
    response = client.put('/posts/4',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'Trying to hack'
        }
    )
    # Should fail with ownership check
    assert response.status_code in [403, 404]


def test_update_any_post_as_editor(client, tokens):
    """Test that editor can update any post."""
    response = client.put('/posts/1',
        headers=get_auth_header(tokens['editor']),
        json={
            'title': 'Editor Updated Title'
        }
    )
    assert response.status_code == 200


def test_delete_own_post(client, tokens):
    """Test deleting own post."""
    # Create a post first
    create_response = client.post('/posts',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'To Delete',
            'content': 'Will be deleted',
            'status': 'draft'
        }
    )
    post_id = create_response.json['post']['id']
    
    # Delete it
    response = client.delete(f'/posts/{post_id}',
        headers=get_auth_header(tokens['author'])
    )
    assert response.status_code == 200


def test_publish_post_as_editor(client, tokens):
    """Test publishing a post as editor."""
    # Create draft post
    create_response = client.post('/posts',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'Draft Post',
            'content': 'Draft content',
            'status': 'draft'
        }
    )
    post_id = create_response.json['post']['id']
    
    # Publish as editor
    response = client.post(f'/posts/{post_id}/publish',
        headers=get_auth_header(tokens['editor'])
    )
    assert response.status_code == 200
    assert response.json['post']['status'] == 'published'


# ==================== Comment Tests ====================

def test_list_comments(client):
    """Test listing comments for a post."""
    response = client.get('/posts/1/comments')
    assert response.status_code == 200
    data = response.json
    assert 'comments' in data


def test_create_comment(client, tokens):
    """Test creating a comment."""
    response = client.post('/posts/1/comments',
        headers=get_auth_header(tokens['reader']),
        json={
            'content': 'Great post!'
        }
    )
    assert response.status_code == 201
    data = response.json
    assert data['message'] == 'Comment created successfully'


def test_create_comment_without_auth_fails(client):
    """Test that comment creation requires auth."""
    response = client.post('/posts/1/comments', json={
        'content': 'Should fail'
    })
    assert response.status_code == 401


def test_delete_own_comment(client, tokens):
    """Test deleting own comment."""
    # Create comment
    create_response = client.post('/posts/1/comments',
        headers=get_auth_header(tokens['reader']),
        json={
            'content': 'To be deleted'
        }
    )
    comment_id = create_response.json['comment']['id']
    
    # Delete it
    response = client.delete(f'/comments/{comment_id}',
        headers=get_auth_header(tokens['reader'])
    )
    assert response.status_code == 200


# ==================== Admin Tests ====================

def test_list_users_as_admin(client, tokens):
    """Test listing users as admin."""
    response = client.get('/admin/users',
        headers=get_auth_header(tokens['admin'])
    )
    assert response.status_code == 200
    data = response.json
    assert 'users' in data
    assert data['count'] > 0


def test_list_users_as_non_admin_fails(client, tokens):
    """Test that non-admin cannot list users."""
    response = client.get('/admin/users',
        headers=get_auth_header(tokens['author'])
    )
    assert response.status_code == 403


def test_update_user_role_as_admin(client, tokens):
    """Test updating user role as admin."""
    # Register new user first
    client.post('/auth/register', json={
        'username': 'roletest',
        'email': 'roletest@example.com',
        'password': 'password123',
        'role': 'reader'
    })
    
    # Get user ID (assuming it's the last created)
    users_response = client.get('/admin/users',
        headers=get_auth_header(tokens['admin'])
    )
    users = users_response.json['users']
    test_user = next((u for u in users if u['username'] == 'roletest'), None)
    
    if test_user:
        # Update role
        response = client.put(f"/admin/users/{test_user['id']}/role",
            headers=get_auth_header(tokens['admin']),
            json={'role': 'author'}
        )
        assert response.status_code == 200


def test_get_stats_as_admin(client, tokens):
    """Test getting system stats as admin."""
    response = client.get('/admin/stats',
        headers=get_auth_header(tokens['admin'])
    )
    assert response.status_code == 200
    data = response.json
    assert 'total_users' in data
    assert 'total_posts' in data
    assert 'total_comments' in data


def test_get_stats_as_non_admin_fails(client, tokens):
    """Test that non-admin cannot get stats."""
    response = client.get('/admin/stats',
        headers=get_auth_header(tokens['reader'])
    )
    assert response.status_code == 403


# ==================== Validation Tests ====================

def test_create_post_missing_fields(client, tokens):
    """Test creating post with missing required fields."""
    response = client.post('/posts',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'Only Title'
        }
    )
    assert response.status_code == 400


def test_create_post_invalid_status(client, tokens):
    """Test creating post with invalid status."""
    response = client.post('/posts',
        headers=get_auth_header(tokens['author']),
        json={
            'title': 'Test',
            'content': 'Test content',
            'status': 'invalid_status'
        }
    )
    assert response.status_code == 400


# ==================== RBAC Integration Tests ====================

def test_rbac_role_hierarchy(client, tokens):
    """Test that admin has all permissions."""
    # Admin should be able to do everything
    
    # Create post
    response = client.post('/posts',
        headers=get_auth_header(tokens['admin']),
        json={
            'title': 'Admin Post',
            'content': 'Admin content',
            'status': 'published'
        }
    )
    assert response.status_code == 201
    
    # Admin can access admin endpoints
    response = client.get('/admin/users',
        headers=get_auth_header(tokens['admin'])
    )
    assert response.status_code == 200


def test_rbac_permission_denied(client, tokens):
    """Test permission denial for unauthorized actions."""
    # Reader trying to create post
    response = client.post('/posts',
        headers=get_auth_header(tokens['reader']),
        json={
            'title': 'Reader Post',
            'content': 'Should fail',
            'status': 'draft'
        }
    )
    assert response.status_code == 403
    assert 'Forbidden' in response.json['error']


# ==================== Error Handling Tests ====================

def test_404_not_found(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404


def test_get_nonexistent_post(client):
    """Test getting non-existent post."""
    response = client.get('/posts/99999')
    assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
