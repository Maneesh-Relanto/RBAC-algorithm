"""
FastAPI Blog API — Integration Tests
======================================
All tests use FastAPI's built-in TestClient (synchronous), which is backed by
httpx and does NOT require a running server.

Coverage mirrors the Flask test suite (test-apps/02-flask-blog-api/test_api.py).
Tests are grouped by feature domain and run fully in-memory.
"""
import sys
import os
import pytest

# Make sure we can import the app from this directory
sys.path.insert(0, os.path.dirname(__file__))
# Allow discovery of the RBAC library from ../../src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from fastapi.testclient import TestClient
from app import create_app


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def app():
    """Create a test app (no seed data, clean in-memory state)."""
    return create_app(testing=True)


@pytest.fixture(scope="module")
def client(app):
    """Return a TestClient bound to the test app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def registered_users(client):
    """Register all personas and return {username: token, ...}."""
    credentials = {
        "admin":    {"username": "test_admin",   "email": "tadmin@test.com",  "password": "Admin1234!"},   # NOSONAR
        "editor":   {"username": "test_editor",  "email": "teditor@test.com", "password": "Editor123!"},  # NOSONAR
        "author1":  {"username": "test_author1", "email": "tauth1@test.com",  "password": "Author123!"},  # NOSONAR
        "author2":  {"username": "test_author2", "email": "tauth2@test.com",  "password": "Author456!"},  # NOSONAR
        "reader":   {"username": "test_reader",  "email": "treader@test.com", "password": "Reader123!"},  # NOSONAR
    }
    tokens = {}
    user_ids = {}
    for key, creds in credentials.items():
        r = client.post("/auth/register", json=creds)
        assert r.status_code == 201, r.json()
        data = r.json()
        tokens[key] = data["access_token"]
        user_ids[key] = data["user"]["id"]

    # Promote admin, editor via direct storage (test-only shortcut)
    storage = client.app.state.storage
    rbac = client.app.state.rbac
    for key, role in [("admin", "admin"), ("editor", "editor"), ("author1", "author"), ("author2", "author")]:
        uid = user_ids[key]
        storage.update_user_role(uid, role)
        rbac_uid = f"user_{uid}"
        try:
            rbac.revoke_role(rbac_uid, "role_reader")
        except Exception:
            pass
        rbac.assign_role(rbac_uid, f"role_{role}")

    # Re-login to get fresh tokens with updated roles in the JWT
    credentials_map = {
        "admin":   ("test_admin",   "Admin1234!"),
        "editor":  ("test_editor",  "Editor123!"),
        "author1": ("test_author1", "Author123!"),
        "author2": ("test_author2", "Author456!"),
        "reader":  ("test_reader",  "Reader123!"),
    }
    for key, (username, password) in credentials_map.items():
        r = client.post("/auth/login", json={"username": username, "password": password})
        assert r.status_code == 200, r.json()
        tokens[key] = r.json()["access_token"]

    return {"tokens": tokens, "user_ids": user_ids}


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Health & Root
# ============================================================================

class TestHealthAndRoot:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "healthy"
        assert "service" in body

    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert "endpoints" in body


# ============================================================================
# Authentication
# ============================================================================

class TestAuth:
    def test_register_success(self, client):
        r = client.post("/auth/register", json={
            "username": "newuser_auth",
            "email": "newuser_auth@test.com",
            "password": "NewPass123!",  # NOSONAR
        })
        assert r.status_code == 201
        body = r.json()
        assert "access_token" in body
        assert body["user"]["username"] == "newuser_auth"
        assert body["user"]["role"] == "reader"

    def test_register_duplicate_username(self, client, registered_users):
        # reader already registered; try same username
        r = client.post("/auth/register", json={
            "username": "test_reader",
            "email": "other@test.com",
            "password": "Pass1234!",  # NOSONAR
        })
        assert r.status_code == 409

    def test_register_duplicate_email(self, client, registered_users):
        r = client.post("/auth/register", json={
            "username": "different_name",
            "email": "treader@test.com",
            "password": "Pass1234!",  # NOSONAR
        })
        assert r.status_code == 409

    def test_login_success(self, client):
        client.post("/auth/register", json={
            "username": "login_test_user",
            "email": "logintest@test.com",
            "password": "LoginPass1!",  # NOSONAR
        })
        r = client.post("/auth/login", json={"username": "login_test_user", "password": "LoginPass1!"})  # NOSONAR
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body

    def test_login_wrong_password(self, client, registered_users):
        r = client.post("/auth/login", json={"username": "test_reader", "password": "wrongpassword"})  # NOSONAR
        assert r.status_code == 401

    def test_login_nonexistent_user(self, client):
        r = client.post("/auth/login", json={"username": "ghost_user", "password": "whatever"})  # NOSONAR
        assert r.status_code == 401

    def test_get_me(self, client, registered_users):
        token = registered_users["tokens"]["reader"]
        r = client.get("/auth/me", headers=auth_header(token))
        assert r.status_code == 200
        assert r.json()["username"] == "test_reader"

    def test_get_me_unauthenticated(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_get_me_bad_token(self, client):
        r = client.get("/auth/me", headers={"Authorization": "Bearer this.is.not.valid"})
        assert r.status_code == 401


# ============================================================================
# Posts
# ============================================================================

class TestPosts:
    @pytest.fixture(scope="class")
    def post_id(self, client, registered_users):
        """Create one post as author1 and return its ID."""
        token = registered_users["tokens"]["author1"]
        r = client.post("/posts", json={
            "title": "RBAC Deep Dive",
            "content": "A comprehensive look at role-based access control.",
            "tags": ["rbac", "security"],
        }, headers=auth_header(token))
        assert r.status_code == 201, r.json()
        return r.json()["id"]

    def test_list_posts_unauthenticated_sees_published_only(self, client, registered_users):
        # Publish one post as editor so there is something visible
        tok = registered_users["tokens"]["editor"]
        r = client.post("/posts", json={
            "title": "Published by Editor",
            "content": "Editor content",
            "status": "published",
        }, headers=auth_header(tok))
        assert r.status_code == 201

        posts = client.get("/posts").json()["posts"]
        for p in posts:
            assert p["status"] == "published"

    def test_create_post_as_author(self, client, registered_users, post_id):
        assert post_id is not None

    def test_create_post_as_reader_forbidden(self, client, registered_users):
        token = registered_users["tokens"]["reader"]
        r = client.post("/posts", json={
            "title": "Reader Attempting Post",
            "content": "Should fail.",
        }, headers=auth_header(token))
        assert r.status_code == 403

    def test_create_post_unauthenticated(self, client):
        r = client.post("/posts", json={"title": "Anon", "content": "Anon"})
        assert r.status_code == 401

    def test_get_post(self, client, registered_users):
        # Create and publish a post
        tok = registered_users["tokens"]["author1"]
        r = client.post("/posts", json={
            "title": "Visible Post",
            "content": "Some content",
            "status": "published",
        }, headers=auth_header(tok))
        pid = r.json()["id"]
        r2 = client.get(f"/posts/{pid}")
        assert r2.status_code == 200
        assert r2.json()["id"] == pid

    def test_get_nonexistent_post(self, client):
        r = client.get("/posts/nonexistent_id_xyz")
        assert r.status_code == 404

    def test_update_own_post(self, client, registered_users, post_id):
        token = registered_users["tokens"]["author1"]
        r = client.put(f"/posts/{post_id}", json={"title": "Updated Title"}, headers=auth_header(token))
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Title"

    def test_update_others_post_as_reader_forbidden(self, client, registered_users, post_id):
        token = registered_users["tokens"]["reader"]
        r = client.put(f"/posts/{post_id}", json={"title": "Hacked"}, headers=auth_header(token))
        assert r.status_code == 403

    def test_admin_can_update_any_post(self, client, registered_users, post_id):
        token = registered_users["tokens"]["admin"]
        r = client.put(f"/posts/{post_id}", json={"title": "Admin Updated"}, headers=auth_header(token))
        assert r.status_code == 200

    def test_publish_post_as_editor(self, client, registered_users, post_id):
        tok = registered_users["tokens"]["editor"]
        r = client.put(f"/posts/{post_id}/publish", headers=auth_header(tok))
        assert r.status_code == 200

    def test_publish_post_as_reader_forbidden(self, client, registered_users, post_id):
        tok = registered_users["tokens"]["reader"]
        r = client.put(f"/posts/{post_id}/publish", headers=auth_header(tok))
        assert r.status_code == 403

    def test_delete_others_post_as_author_forbidden(self, client, registered_users, post_id):
        tok = registered_users["tokens"]["author2"]
        r = client.delete(f"/posts/{post_id}", headers=auth_header(tok))
        assert r.status_code == 403

    def test_delete_own_post(self, client, registered_users):
        tok = registered_users["tokens"]["author1"]
        r = client.post("/posts", json={"title": "To Delete", "content": "bye"}, headers=auth_header(tok))
        pid = r.json()["id"]
        r2 = client.delete(f"/posts/{pid}", headers=auth_header(tok))
        assert r2.status_code == 200


# ============================================================================
# Comments
# ============================================================================

class TestComments:
    @pytest.fixture(scope="class")
    def published_post_id(self, client, registered_users):
        tok = registered_users["tokens"]["author1"]
        r = client.post("/posts", json={
            "title": "Post With Comments",
            "content": "Come comment here",
            "status": "published",
        }, headers=auth_header(tok))
        assert r.status_code == 201
        return r.json()["id"]

    def test_add_comment_as_reader(self, client, registered_users, published_post_id):
        tok = registered_users["tokens"]["reader"]
        r = client.post(f"/posts/{published_post_id}/comments",
                        json={"content": "Great post!"},
                        headers=auth_header(tok))
        assert r.status_code == 201
        assert r.json()["content"] == "Great post!"

    def test_add_comment_unauthenticated(self, client, published_post_id):
        r = client.post(f"/posts/{published_post_id}/comments", json={"content": "Anon comment"})
        assert r.status_code == 401

    def test_get_comments(self, client, published_post_id):
        r = client.get(f"/posts/{published_post_id}/comments")
        assert r.status_code == 200
        body = r.json()
        assert "comments" in body
        assert body["total"] >= 1

    def test_delete_own_comment(self, client, registered_users, published_post_id):
        tok = registered_users["tokens"]["reader"]
        r = client.post(f"/posts/{published_post_id}/comments",
                        json={"content": "Will delete this"},
                        headers=auth_header(tok))
        cid = r.json()["id"]
        r2 = client.delete(f"/comments/{cid}", headers=auth_header(tok))
        assert r2.status_code == 200

    def test_delete_others_comment_as_reader_forbidden(self, client, registered_users, published_post_id):
        # author1 adds a comment
        tok_author = registered_users["tokens"]["author1"]
        r = client.post(f"/posts/{published_post_id}/comments",
                        json={"content": "Author comment"},
                        headers=auth_header(tok_author))
        cid = r.json()["id"]
        # reader tries to delete it
        tok_reader = registered_users["tokens"]["reader"]
        r2 = client.delete(f"/comments/{cid}", headers=auth_header(tok_reader))
        assert r2.status_code == 403

    def test_admin_can_delete_any_comment(self, client, registered_users, published_post_id):
        tok_reader = registered_users["tokens"]["reader"]
        r = client.post(f"/posts/{published_post_id}/comments",
                        json={"content": "To be nuked by admin"},
                        headers=auth_header(tok_reader))
        cid = r.json()["id"]
        tok_admin = registered_users["tokens"]["admin"]
        r2 = client.delete(f"/comments/{cid}", headers=auth_header(tok_admin))
        assert r2.status_code == 200


# ============================================================================
# Admin
# ============================================================================

class TestAdmin:
    def test_list_users_as_admin(self, client, registered_users):
        tok = registered_users["tokens"]["admin"]
        r = client.get("/admin/users", headers=auth_header(tok))
        assert r.status_code == 200
        body = r.json()
        assert "users" in body
        assert body["total"] >= 1

    def test_list_users_as_reader_forbidden(self, client, registered_users):
        tok = registered_users["tokens"]["reader"]
        r = client.get("/admin/users", headers=auth_header(tok))
        assert r.status_code == 403

    def test_list_users_unauthenticated(self, client):
        r = client.get("/admin/users")
        assert r.status_code == 401

    def test_update_user_role_as_admin(self, client, registered_users):
        tok = registered_users["tokens"]["admin"]
        uid = registered_users["user_ids"]["reader"]
        r = client.put(f"/admin/users/{uid}/role",
                       json={"role": "author"},
                       headers=auth_header(tok))
        assert r.status_code == 200
        assert r.json()["role"] == "author"
        # Restore
        client.put(f"/admin/users/{uid}/role",
                   json={"role": "reader"},
                   headers=auth_header(tok))

    def test_update_own_role_forbidden(self, client, registered_users):
        tok = registered_users["tokens"]["admin"]
        uid = registered_users["user_ids"]["admin"]
        r = client.put(f"/admin/users/{uid}/role",
                       json={"role": "reader"},
                       headers=auth_header(tok))
        assert r.status_code == 400

    def test_update_role_invalid_value(self, client, registered_users):
        tok = registered_users["tokens"]["admin"]
        uid = registered_users["user_ids"]["reader"]
        r = client.put(f"/admin/users/{uid}/role",
                       json={"role": "superuser"},
                       headers=auth_header(tok))
        # Pydantic validation returns 422 Unprocessable Entity for invalid enum values
        assert r.status_code in (400, 422)

    def test_get_stats_as_admin(self, client, registered_users):
        tok = registered_users["tokens"]["admin"]
        r = client.get("/admin/stats", headers=auth_header(tok))
        assert r.status_code == 200
        body = r.json()
        assert "total_users" in body
        assert "total_posts" in body

    def test_get_stats_as_editor(self, client, registered_users):
        tok = registered_users["tokens"]["editor"]
        r = client.get("/admin/stats", headers=auth_header(tok))
        assert r.status_code == 200

    def test_get_stats_as_reader_forbidden(self, client, registered_users):
        tok = registered_users["tokens"]["reader"]
        r = client.get("/admin/stats", headers=auth_header(tok))
        assert r.status_code == 403
