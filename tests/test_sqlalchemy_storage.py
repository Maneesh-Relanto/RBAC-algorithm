"""Tests for SQLAlchemyStorage adapter.

Uses an in-memory SQLite database so no external service is required.
The test surface mirrors test_storage.py (MemoryStorage) to ensure both
backends are fully interchangeable.
"""

import pytest
from datetime import datetime, timedelta, timezone

from rbac.storage.sqlalchemy_adapter import SQLAlchemyStorage
from rbac.core.models import User, Permission, Resource, EntityStatus
from rbac.core.models.role import Role, RoleAssignment
from rbac.core.exceptions import (
    DuplicateEntityError,
    PermissionNotFound,
    ResourceNotFound,
    RoleNotFound,
    StorageError,
    UserNotFound,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def storage():
    """Fresh in-memory SQLite storage for each test."""
    s = SQLAlchemyStorage("sqlite:///:memory:")
    s.initialize()
    yield s
    s.dispose()


@pytest.fixture
def domain():
    return "test_domain"


@pytest.fixture
def sample_user(domain):
    return User(
        id="user_alice",
        email="alice@example.com",
        name="Alice",
        domain=domain,
    )


@pytest.fixture
def sample_role(domain):
    return Role(
        id="role_admin",
        name="Administrator",
        description="Full access",
        domain=domain,
    )


@pytest.fixture
def sample_permission():
    return Permission(
        id="perm_post_read",
        resource_type="post",
        action="read",
        description="Read blog posts",
    )


@pytest.fixture
def sample_resource(domain):
    return Resource(
        id="resource_doc1",
        type="document",
        domain=domain,
    )


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

class TestLifecycle:
    def test_initialize_creates_tables(self):
        """initialize() must succeed and be idempotent."""
        s = SQLAlchemyStorage("sqlite:///:memory:")
        s.initialize()
        s.initialize()  # second call must not raise
        s.dispose()

    def test_get_stats_empty(self, storage):
        stats = storage.get_stats()
        assert stats["users"] == 0
        assert stats["roles"] == 0
        assert stats["permissions"] == 0
        assert stats["resources"] == 0
        assert stats["role_assignments"] == 0


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

class TestUserCRUD:
    def test_create_and_get(self, storage, sample_user):
        created = storage.create_user(sample_user)
        assert created.id == sample_user.id
        fetched = storage.get_user(sample_user.id)
        assert fetched.id == sample_user.id
        assert fetched.email == sample_user.email

    def test_create_duplicate_raises(self, storage, sample_user):
        storage.create_user(sample_user)
        with pytest.raises(DuplicateEntityError):
            storage.create_user(sample_user)

    def test_get_missing_raises(self, storage):
        with pytest.raises(UserNotFound):
            storage.get_user("user_nonexistent")

    def test_update_user(self, storage, sample_user):
        storage.create_user(sample_user)
        from dataclasses import replace
        updated = replace(sample_user, email="updated@example.com", name="Alice Updated")
        result = storage.update_user(updated)
        assert result.email == "updated@example.com"
        assert result.name == "Alice Updated"
        # Verify persisted
        fetched = storage.get_user(sample_user.id)
        assert fetched.email == "updated@example.com"

    def test_update_missing_raises(self, storage, sample_user):
        with pytest.raises(UserNotFound):
            storage.update_user(sample_user)

    def test_delete_user(self, storage, sample_user):
        storage.create_user(sample_user)
        result = storage.delete_user(sample_user.id)
        assert result is True
        with pytest.raises(UserNotFound):
            storage.get_user(sample_user.id)

    def test_delete_missing_raises(self, storage):
        with pytest.raises(UserNotFound):
            storage.delete_user("user_ghost")

    def test_list_users_no_filter(self, storage, domain):
        for i in range(3):
            storage.create_user(
                User(id=f"user_{i}", email=f"u{i}@x.com", name=f"User {i}", domain=domain)
            )
        users = storage.list_users()
        assert len(users) == 3

    def test_list_users_domain_filter(self, storage):
        storage.create_user(User(id="user_a", email="a@x.com", name="A", domain="d1"))
        storage.create_user(User(id="user_b", email="b@x.com", name="B", domain="d2"))
        assert len(storage.list_users(domain="d1")) == 1
        assert len(storage.list_users(domain="d2")) == 1

    def test_list_users_excludes_deleted(self, storage, sample_user):
        storage.create_user(sample_user)
        storage.delete_user(sample_user.id)
        assert storage.list_users() == []

    def test_list_pagination(self, storage, domain):
        for i in range(5):
            storage.create_user(
                User(id=f"user_{i}", email=f"u{i}@x.com", name=f"User {i}", domain=domain)
            )
        page1 = storage.list_users(limit=3, offset=0)
        page2 = storage.list_users(limit=3, offset=3)
        assert len(page1) == 3
        assert len(page2) == 2

    def test_stats_counts_active_only(self, storage, sample_user):
        storage.create_user(sample_user)
        assert storage.get_stats()["users"] == 1
        storage.delete_user(sample_user.id)
        assert storage.get_stats()["users"] == 0


# ---------------------------------------------------------------------------
# Role CRUD
# ---------------------------------------------------------------------------

class TestRoleCRUD:
    def test_create_and_get(self, storage, sample_role):
        storage.create_role(sample_role)
        fetched = storage.get_role(sample_role.id)
        assert fetched.id == sample_role.id
        assert fetched.name == sample_role.name

    def test_create_duplicate_raises(self, storage, sample_role):
        storage.create_role(sample_role)
        with pytest.raises(DuplicateEntityError):
            storage.create_role(sample_role)

    def test_get_missing_raises(self, storage):
        with pytest.raises(RoleNotFound):
            storage.get_role("role_ghost")

    def test_delete_role(self, storage, sample_role):
        storage.create_role(sample_role)
        assert storage.delete_role(sample_role.id) is True
        with pytest.raises(RoleNotFound):
            storage.get_role(sample_role.id)

    def test_delete_role_with_children_raises(self, storage, domain):
        parent = Role(id="role_parent", name="Parent", domain=domain)
        child = Role(id="role_child", name="Child", parent_id="role_parent", domain=domain)
        storage.create_role(parent)
        storage.create_role(child)
        with pytest.raises(StorageError):
            storage.delete_role("role_parent")

    def test_role_with_permissions(self, storage, sample_permission):
        storage.create_permission(sample_permission)
        role = Role(
            id="role_reader",
            name="Reader",
            permissions={sample_permission.id},
        )
        storage.create_role(role)
        fetched = storage.get_role(role.id)
        assert sample_permission.id in fetched.permissions

    def test_update_role_permissions(self, storage, sample_permission):
        storage.create_permission(sample_permission)
        role = Role(id="role_r", name="R", permissions={sample_permission.id})
        storage.create_role(role)

        new_perm = Permission(id="perm_post_write", resource_type="post", action="write")
        storage.create_permission(new_perm)

        from dataclasses import replace
        updated = replace(role, permissions={new_perm.id})
        storage.update_role(updated)

        fetched = storage.get_role(role.id)
        assert new_perm.id in fetched.permissions
        assert sample_permission.id not in fetched.permissions

    def test_circular_hierarchy_raises(self, storage, domain):
        r1 = Role(id="role_1", name="R1", domain=domain)
        r2 = Role(id="role_2", name="R2", parent_id="role_1", domain=domain)
        storage.create_role(r1)
        storage.create_role(r2)
        # Trying to make r1 a child of r2 would create a cycle
        from rbac.core.exceptions import CircularDependencyError
        from dataclasses import replace
        r1_updated = replace(r1, parent_id="role_2")
        with pytest.raises(CircularDependencyError):
            storage.update_role(r1_updated)

    def test_list_roles(self, storage, domain):
        for i in range(3):
            storage.create_role(Role(id=f"role_{i}", name=f"Role{i}", domain=domain))
        roles = storage.list_roles(domain=domain)
        assert len(roles) == 3

    def test_list_roles_excludes_deleted(self, storage, domain):
        r = Role(id="role_tmp", name="Tmp", domain=domain)
        storage.create_role(r)
        storage.delete_role(r.id)
        assert storage.list_roles(domain=domain) == []


# ---------------------------------------------------------------------------
# Permission CRUD
# ---------------------------------------------------------------------------

class TestPermissionCRUD:
    def test_create_and_get(self, storage, sample_permission):
        storage.create_permission(sample_permission)
        fetched = storage.get_permission(sample_permission.id)
        assert fetched.id == sample_permission.id
        assert fetched.resource_type == sample_permission.resource_type
        assert fetched.action == sample_permission.action

    def test_create_duplicate_raises(self, storage, sample_permission):
        storage.create_permission(sample_permission)
        with pytest.raises(DuplicateEntityError):
            storage.create_permission(sample_permission)

    def test_get_missing_raises(self, storage):
        with pytest.raises(PermissionNotFound):
            storage.get_permission("perm_ghost")

    def test_delete_permission(self, storage, sample_permission):
        storage.create_permission(sample_permission)
        assert storage.delete_permission(sample_permission.id) is True
        with pytest.raises(PermissionNotFound):
            storage.get_permission(sample_permission.id)

    def test_delete_permission_removes_from_roles(self, storage, sample_permission):
        storage.create_permission(sample_permission)
        role = Role(
            id="role_r",
            name="R",
            permissions={sample_permission.id},
        )
        storage.create_role(role)
        storage.delete_permission(sample_permission.id)
        fetched = storage.get_role(role.id)
        assert sample_permission.id not in fetched.permissions

    def test_list_permissions(self, storage):
        for i in range(4):
            storage.create_permission(
                Permission(id=f"perm_{i}", resource_type="doc", action=f"act{i}")
            )
        perms = storage.list_permissions()
        assert len(perms) == 4

    def test_list_permissions_filter_resource_type(self, storage):
        storage.create_permission(Permission(id="perm_a", resource_type="doc", action="read"))
        storage.create_permission(Permission(id="perm_b", resource_type="user", action="read"))
        assert len(storage.list_permissions(resource_type="doc")) == 1


# ---------------------------------------------------------------------------
# Resource CRUD
# ---------------------------------------------------------------------------

class TestResourceCRUD:
    def test_create_and_get(self, storage, sample_resource):
        storage.create_resource(sample_resource)
        fetched = storage.get_resource(sample_resource.id)
        assert fetched.id == sample_resource.id
        assert fetched.type == sample_resource.type

    def test_create_duplicate_raises(self, storage, sample_resource):
        storage.create_resource(sample_resource)
        with pytest.raises(DuplicateEntityError):
            storage.create_resource(sample_resource)

    def test_get_missing_raises(self, storage):
        with pytest.raises(ResourceNotFound):
            storage.get_resource("resource_ghost")

    def test_delete_resource(self, storage, sample_resource):
        storage.create_resource(sample_resource)
        assert storage.delete_resource(sample_resource.id) is True
        with pytest.raises(ResourceNotFound):
            storage.get_resource(sample_resource.id)

    def test_list_resources_with_filters(self, storage):
        storage.create_resource(Resource(id="resource_d1", type="document", domain="d1"))
        storage.create_resource(Resource(id="resource_d2", type="image", domain="d2"))
        assert len(storage.list_resources(resource_type="document")) == 1
        assert len(storage.list_resources(domain="d2")) == 1


# ---------------------------------------------------------------------------
# Role assignments
# ---------------------------------------------------------------------------

class TestRoleAssignments:
    def test_assign_and_get_user_roles(
        self, storage, sample_user, sample_role
    ):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        assignment = RoleAssignment(
            user_id=sample_user.id,
            role_id=sample_role.id,
        )
        storage.assign_role(assignment)
        roles = storage.get_user_roles(sample_user.id)
        assert any(r.id == sample_role.id for r in roles)

    def test_duplicate_assignment_raises(
        self, storage, sample_user, sample_role
    ):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        assignment = RoleAssignment(
            user_id=sample_user.id,
            role_id=sample_role.id,
        )
        storage.assign_role(assignment)
        with pytest.raises(DuplicateEntityError):
            storage.assign_role(assignment)

    def test_assign_missing_user_raises(self, storage, sample_role):
        storage.create_role(sample_role)
        with pytest.raises(UserNotFound):
            storage.assign_role(
                RoleAssignment(user_id="user_ghost", role_id=sample_role.id)
            )

    def test_assign_missing_role_raises(self, storage, sample_user):
        storage.create_user(sample_user)
        with pytest.raises(RoleNotFound):
            storage.assign_role(
                RoleAssignment(user_id=sample_user.id, role_id="role_ghost")
            )

    def test_revoke_role(self, storage, sample_user, sample_role):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        storage.assign_role(
            RoleAssignment(user_id=sample_user.id, role_id=sample_role.id)
        )
        assert storage.revoke_role(sample_user.id, sample_role.id) is True
        roles = storage.get_user_roles(sample_user.id)
        assert not any(r.id == sample_role.id for r in roles)

    def test_revoke_nonexistent_returns_false(
        self, storage, sample_user, sample_role
    ):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        assert storage.revoke_role(sample_user.id, sample_role.id) is False

    def test_get_role_users(self, storage, sample_user, sample_role):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        storage.assign_role(
            RoleAssignment(user_id=sample_user.id, role_id=sample_role.id)
        )
        users = storage.get_role_users(sample_role.id)
        assert any(u.id == sample_user.id for u in users)

    def test_expired_assignment_excluded(
        self, storage, sample_user, sample_role
    ):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        storage.assign_role(
            RoleAssignment(
                user_id=sample_user.id,
                role_id=sample_role.id,
                expires_at=past,
            )
        )
        roles = storage.get_user_roles(sample_user.id)
        assert not any(r.id == sample_role.id for r in roles)

    def test_active_assignment_with_future_expiry(
        self, storage, sample_user, sample_role
    ):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        future = datetime.now(timezone.utc) + timedelta(hours=24)
        storage.assign_role(
            RoleAssignment(
                user_id=sample_user.id,
                role_id=sample_role.id,
                expires_at=future,
            )
        )
        roles = storage.get_user_roles(sample_user.id)
        assert any(r.id == sample_role.id for r in roles)

    def test_domain_scoped_assignment(
        self, storage, sample_user, sample_role
    ):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        storage.assign_role(
            RoleAssignment(
                user_id=sample_user.id,
                role_id=sample_role.id,
                domain="domain_a",
            )
        )
        # Should appear when filtering by matching domain
        assert len(storage.get_user_roles(sample_user.id, domain="domain_a")) == 1
        # Should NOT appear when filtering by different domain
        assert len(storage.get_user_roles(sample_user.id, domain="domain_b")) == 0

    def test_delete_user_removes_assignments(
        self, storage, sample_user, sample_role
    ):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        storage.assign_role(
            RoleAssignment(user_id=sample_user.id, role_id=sample_role.id)
        )
        storage.delete_user(sample_user.id)
        # Assignment should be gone: stats confirm
        assert storage.get_stats()["role_assignments"] == 0


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

class TestUtility:
    def test_clear_all(self, storage, sample_user, sample_role, sample_permission):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        storage.create_permission(sample_permission)
        storage.clear_all()
        stats = storage.get_stats()
        assert all(v == 0 for v in stats.values())

    def test_full_stats(self, storage, sample_user, sample_role, sample_permission):
        storage.create_user(sample_user)
        storage.create_role(sample_role)
        storage.create_permission(sample_permission)
        storage.assign_role(
            RoleAssignment(user_id=sample_user.id, role_id=sample_role.id)
        )
        stats = storage.get_stats()
        assert stats["users"] == 1
        assert stats["roles"] == 1
        assert stats["permissions"] == 1
        assert stats["role_assignments"] == 1


# ---------------------------------------------------------------------------
# Persistence (write → new session → read)
# ---------------------------------------------------------------------------

class TestPersistence:
    """Verify data survives across separate Storage instances on a file DB."""

    def test_data_persists_across_instances(self, tmp_path):
        db_url = f"sqlite:///{tmp_path}/rbac.db"

        s1 = SQLAlchemyStorage(db_url)
        s1.initialize()
        user = User(id="user_persist", email="p@p.com", name="Persistent")
        s1.create_user(user)
        s1.dispose()

        s2 = SQLAlchemyStorage(db_url)
        s2.initialize()
        fetched = s2.get_user("user_persist")
        assert fetched.email == "p@p.com"
        s2.dispose()
