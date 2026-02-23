"""SQLAlchemy storage adapter for RBAC system.

Provides a production-ready, persistent storage backend using SQLAlchemy 2.x.
Supports SQLite (development/testing), PostgreSQL, and MySQL.

Usage::

    from rbac.storage.sqlalchemy_adapter import SQLAlchemyStorage

    # SQLite – local file
    storage = SQLAlchemyStorage("sqlite:///rbac.db")

    # PostgreSQL
    storage = SQLAlchemyStorage(
        "postgresql+psycopg2://user:pass@localhost:5432/mydb"
    )

    # MySQL
    storage = SQLAlchemyStorage(
        "mysql+pymysql://user:pass@localhost:3306/mydb"
    )

    # In-memory SQLite (ideal for tests)
    storage = SQLAlchemyStorage("sqlite:///:memory:")

    storage.initialize()          # creates tables
    storage.create_user(user)
    storage.dispose()             # clean up connection pool
"""

from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    delete,
    select,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from .base import BaseStorage
from ..core.models import EntityStatus, Permission, Resource, User
from ..core.models.role import Role, RoleAssignment
from ..core.exceptions import (
    DuplicateEntityError,
    PermissionNotFound,
    ResourceNotFound,
    RoleNotFound,
    StorageError,
    UserNotFound,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ORM declarations
# ---------------------------------------------------------------------------

# FK target constant – avoids repeating the table.column string literal
_FK_ROLES_ID = "rbac_roles.id"


class _Base(DeclarativeBase):
    """Shared declarative base for all RBAC ORM models."""


# Many-to-many junction: role ↔ permission
_role_permissions = Table(
    "rbac_role_permissions",
    _Base.metadata,
    Column("role_id", String(255), ForeignKey(_FK_ROLES_ID, ondelete="CASCADE"), nullable=False),
    Column("permission_id", String(255), ForeignKey("rbac_permissions.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
)


class _UserRow(_Base):
    """ORM model for the rbac_users table."""

    __tablename__ = "rbac_users"
    __table_args__ = (
        Index("ix_rbac_users_domain", "domain"),
        Index("ix_rbac_users_email", "email"),
    )

    id = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    attributes_json = Column(Text, nullable=False, default="{}")
    status = Column(String(50), nullable=False, default="active")
    domain = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class _RoleRow(_Base):
    """ORM model for the rbac_roles table."""

    __tablename__ = "rbac_roles"
    __table_args__ = (
        Index("ix_rbac_roles_domain", "domain"),
    )

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(String(255), ForeignKey(_FK_ROLES_ID, ondelete="SET NULL"), nullable=True)
    domain = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="active")
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class _PermissionRow(_Base):
    """ORM model for the rbac_permissions table."""

    __tablename__ = "rbac_permissions"
    __table_args__ = (
        Index("ix_rbac_permissions_resource_type", "resource_type"),
        UniqueConstraint("resource_type", "action", name="uq_permission_resource_action"),
    )

    id = Column(String(255), primary_key=True)
    resource_type = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    conditions_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime(timezone=True), nullable=False)


class _ResourceRow(_Base):
    """ORM model for the rbac_resources table."""

    __tablename__ = "rbac_resources"
    __table_args__ = (
        Index("ix_rbac_resources_type", "type"),
        Index("ix_rbac_resources_domain", "domain"),
    )

    id = Column(String(255), primary_key=True)
    type = Column(String(255), nullable=False)
    attributes_json = Column(Text, nullable=False, default="{}")
    parent_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="active")
    domain = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class _RoleAssignmentRow(_Base):
    """ORM model for the rbac_role_assignments table."""

    __tablename__ = "rbac_role_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "domain", name="uq_role_assignment"),
        Index("ix_rbac_role_assignments_user", "user_id"),
        Index("ix_rbac_role_assignments_role", "role_id"),
    )

    id = Column(String(255), primary_key=True)  # composite surrogate
    user_id = Column(String(255), ForeignKey("rbac_users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(String(255), ForeignKey(_FK_ROLES_ID, ondelete="CASCADE"), nullable=False)
    domain = Column(String(255), nullable=True)
    granted_by = Column(String(255), nullable=True)
    granted_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_json(obj: Any) -> str:
    return json.dumps(obj, default=str)


def _from_json(s: str) -> Any:
    try:
        return json.loads(s) if s else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def _assignment_pk(user_id: str, role_id: str, domain: Optional[str]) -> str:
    return f"{user_id}|{role_id}|{domain or ''}"


# Domain model → ORM row
def _user_to_row(user: User) -> _UserRow:
    return _UserRow(
        id=user.id,
        email=user.email,
        name=user.name,
        attributes_json=_to_json(user.attributes),
        status=user.status.value,
        domain=user.domain,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _role_to_row(role: Role) -> _RoleRow:
    return _RoleRow(
        id=role.id,
        name=role.name,
        description=role.description,
        parent_id=role.parent_id,
        domain=role.domain,
        status=role.status.value,
        metadata_json=_to_json(role.metadata),
        created_at=role.created_at,
        updated_at=role.updated_at,
    )


def _permission_to_row(permission: Permission) -> _PermissionRow:
    return _PermissionRow(
        id=permission.id,
        resource_type=permission.resource_type,
        action=permission.action,
        description=permission.description,
        conditions_json=_to_json(permission.conditions),
        created_at=permission.created_at,
    )


def _resource_to_row(resource: Resource) -> _ResourceRow:
    return _ResourceRow(
        id=resource.id,
        type=resource.type,
        attributes_json=_to_json(resource.attributes),
        parent_id=resource.parent_id,
        status=resource.status.value,
        domain=resource.domain,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
    )


def _assignment_to_row(assignment: RoleAssignment) -> _RoleAssignmentRow:
    return _RoleAssignmentRow(
        id=_assignment_pk(assignment.user_id, assignment.role_id, assignment.domain),
        user_id=assignment.user_id,
        role_id=assignment.role_id,
        domain=assignment.domain,
        granted_by=assignment.granted_by,
        granted_at=assignment.granted_at,
        expires_at=assignment.expires_at,
        metadata_json=_to_json(assignment.metadata),
    )


# ORM row → domain model
def _row_to_user(row: _UserRow) -> User:
    return User(
        id=row.id,
        email=row.email,
        name=row.name,
        attributes=_from_json(row.attributes_json),
        status=EntityStatus(row.status),
        domain=row.domain,
        created_at=_ensure_utc(row.created_at),
        updated_at=_ensure_utc(row.updated_at),
    )


def _row_to_role(row: _RoleRow, permissions: set) -> Role:
    return Role(
        id=row.id,
        name=row.name,
        description=row.description,
        permissions=permissions,
        parent_id=row.parent_id,
        domain=row.domain,
        status=EntityStatus(row.status),
        metadata=_from_json(row.metadata_json),
        created_at=_ensure_utc(row.created_at),
        updated_at=_ensure_utc(row.updated_at),
    )


def _row_to_permission(row: _PermissionRow) -> Permission:
    return Permission(
        id=row.id,
        resource_type=row.resource_type,
        action=row.action,
        description=row.description,
        conditions=_from_json(row.conditions_json),
        created_at=_ensure_utc(row.created_at),
    )


def _row_to_resource(row: _ResourceRow) -> Resource:
    return Resource(
        id=row.id,
        type=row.type,
        attributes=_from_json(row.attributes_json),
        parent_id=row.parent_id,
        status=EntityStatus(row.status),
        domain=row.domain,
        created_at=_ensure_utc(row.created_at),
        updated_at=_ensure_utc(row.updated_at),
    )


def _row_to_assignment(row: _RoleAssignmentRow) -> RoleAssignment:
    return RoleAssignment(
        user_id=row.user_id,
        role_id=row.role_id,
        domain=row.domain,
        granted_by=row.granted_by,
        granted_at=_ensure_utc(row.granted_at),
        expires_at=_ensure_utc(row.expires_at) if row.expires_at else None,
        metadata=_from_json(row.metadata_json),
    )


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Attach UTC timezone to naive datetimes returned by some drivers."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# Storage adapter
# ---------------------------------------------------------------------------

class SQLAlchemyStorage(BaseStorage):
    """Persistent RBAC storage backed by any SQLAlchemy-supported database.

    Supports SQLite, PostgreSQL, and MySQL out of the box.  Pass any valid
    SQLAlchemy connection URL to the constructor. Call :meth:`initialize`
    before first use to create the tables. Call :meth:`dispose` on shutdown
    to release the connection pool.

    All public methods mirror the :class:`~rbac.storage.memory.MemoryStorage`
    API so the two are drop-in replacements for each other.

    Args:
        database_url: SQLAlchemy connection string.
        echo: If True, SQL statements are logged (useful for debugging).
        pool_size: Connection pool size (ignored for SQLite).
        max_overflow: Extra connections allowed above *pool_size*.

    Examples::

        storage = SQLAlchemyStorage("sqlite:///rbac.db")
        storage.initialize()

        storage = SQLAlchemyStorage(
            "postgresql+psycopg2://user:p@localhost/mydb",
            pool_size=5,
        )
        storage.initialize()
    """

    def __init__(
        self,
        database_url: str,
        *,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self._url = database_url
        is_sqlite = database_url.startswith("sqlite")

        kwargs: Dict[str, Any] = {"echo": echo}
        if not is_sqlite:
            kwargs["pool_size"] = pool_size
            kwargs["max_overflow"] = max_overflow
        else:
            # Required for SQLite in-memory usage across multiple threads
            kwargs["connect_args"] = {"check_same_thread": False}

        self._engine = create_engine(database_url, **kwargs)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Create all RBAC tables if they do not already exist."""
        _Base.metadata.create_all(self._engine)
        logger.info("SQLAlchemyStorage initialized on %s", self._url)

    def dispose(self) -> None:
        """Dispose the connection pool. Call on application shutdown."""
        self._engine.dispose()
        logger.info("SQLAlchemyStorage connection pool disposed")

    def _validate_role_assignment(self, assignment: RoleAssignment) -> None:
        """Override base validator to skip expiry check at the storage layer.

        The base class rejects writing an already-expired assignment, but at
        the persistence level that is valid data (historical records, migrations,
        auditing).  Expiry is enforced when *reading* via :meth:`get_user_roles`.
        All other validation (ID format) is still enforced.
        """
        from ..core.exceptions import ValidationError

        if not assignment.user_id or not assignment.user_id.startswith("user_"):
            raise ValidationError("Valid user ID is required")
        if not assignment.role_id or not assignment.role_id.startswith("role_"):
            raise ValidationError("Valid role ID is required")
        # Note: expiry is intentionally NOT validated here.

    @contextmanager
    def _session(self) -> Generator[Session, None, None]:
        """Provide a transactional session scope."""
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ------------------------------------------------------------------
    # User operations
    # ------------------------------------------------------------------

    def create_user(self, user: User) -> User:
        """Create a new user."""
        self._validate_user(user)
        with self._session() as session:
            if session.get(_UserRow, user.id) is not None:
                raise DuplicateEntityError(f"User {user.id} already exists")
            row = _user_to_row(user)
            session.add(row)
        return user

    def get_user(self, user_id: str) -> User:
        """Retrieve a user by ID. Raises :exc:`UserNotFound` if missing."""
        with self._session() as session:
            row = session.get(_UserRow, user_id)
        if row is None or row.status == EntityStatus.DELETED.value:
            raise UserNotFound(f"User {user_id} not found")
        return _row_to_user(row)

    def update_user(self, user: User) -> User:
        """Update an existing user."""
        self._validate_user(user)
        updated = User(
            id=user.id,
            email=user.email,
            name=user.name,
            attributes=user.attributes,
            status=user.status,
            domain=user.domain,
            created_at=user.created_at,
            updated_at=_utcnow(),
        )
        with self._session() as session:
            row = session.get(_UserRow, user.id)
            if row is None:
                raise UserNotFound(f"User {user.id} not found")
            row.email = updated.email
            row.name = updated.name
            row.attributes_json = _to_json(updated.attributes)
            row.status = updated.status.value
            row.domain = updated.domain
            row.updated_at = updated.updated_at
        return updated

    def delete_user(self, user_id: str) -> bool:
        """Soft-delete a user by marking status as DELETED."""
        with self._session() as session:
            row = session.get(_UserRow, user_id)
            if row is None:
                raise UserNotFound(f"User {user_id} not found")
            row.status = EntityStatus.DELETED.value
            row.updated_at = _utcnow()
            # Remove assignments
            session.execute(
                delete(_RoleAssignmentRow).where(
                    _RoleAssignmentRow.user_id == user_id
                )
            )
        return True

    def list_users(
        self,
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[User]:
        """List active users, optionally filtered by domain."""
        with self._session() as session:
            stmt = select(_UserRow).where(
                _UserRow.status != EntityStatus.DELETED.value
            )
            if domain is not None:
                stmt = stmt.where(_UserRow.domain == domain)
            stmt = stmt.offset(offset).limit(limit)
            rows = session.scalars(stmt).all()
        return [_row_to_user(r) for r in rows]

    # ------------------------------------------------------------------
    # Role operations
    # ------------------------------------------------------------------

    def _load_role_permissions(self, session: Session, role_id: str) -> set:
        stmt = (
            select(_role_permissions.c.permission_id)
            .where(_role_permissions.c.role_id == role_id)
        )
        return set(session.scalars(stmt).all())

    def create_role(self, role: Role) -> Role:
        """Create a new role including its permission associations."""
        self._validate_role(role)
        with self._session() as session:
            if session.get(_RoleRow, role.id) is not None:
                raise DuplicateEntityError(f"Role {role.id} already exists")
            if role.parent_id and session.get(_RoleRow, role.parent_id) is None:
                raise RoleNotFound(f"Parent role {role.parent_id} not found")
            if role.parent_id:
                self._check_circular_hierarchy(
                    role.id,
                    role.parent_id,
                    lambda rid: self._get_role_row(rid),
                )
            session.add(_role_to_row(role))
            for perm_id in role.permissions:
                session.execute(
                    _role_permissions.insert().values(
                        role_id=role.id, permission_id=perm_id
                    )
                )
        return role

    def _get_role_row(self, role_id: str) -> Optional[Role]:
        """Helper used by circular hierarchy check."""
        with self._session() as session:
            row = session.get(_RoleRow, role_id)
            if row is None:
                return None
            perms = self._load_role_permissions(session, role_id)
            return _row_to_role(row, perms)

    def get_role(self, role_id: str) -> Role:
        """Retrieve a role by ID. Raises :exc:`RoleNotFound` if missing."""
        with self._session() as session:
            row = session.get(_RoleRow, role_id)
            if row is None or row.status == EntityStatus.DELETED.value:
                raise RoleNotFound(f"Role {role_id} not found")
            perms = self._load_role_permissions(session, role_id)
        return _row_to_role(row, perms)

    def update_role(self, role: Role) -> Role:
        """Update an existing role and its permission set."""
        self._validate_role(role)
        updated_at = _utcnow()
        with self._session() as session:
            row = session.get(_RoleRow, role.id)
            if row is None:
                raise RoleNotFound(f"Role {role.id} not found")
            if role.parent_id and role.parent_id != row.parent_id:
                self._check_circular_hierarchy(
                    role.id,
                    role.parent_id,
                    lambda rid: self._get_role_row(rid),
                )
            row.name = role.name
            row.description = role.description
            row.parent_id = role.parent_id
            row.domain = role.domain
            row.status = role.status.value
            row.metadata_json = _to_json(role.metadata)
            row.updated_at = updated_at
            # Sync permissions: clear & re-insert
            session.execute(
                delete(_role_permissions).where(
                    _role_permissions.c.role_id == role.id
                )
            )
            for perm_id in role.permissions:
                session.execute(
                    _role_permissions.insert().values(
                        role_id=role.id, permission_id=perm_id
                    )
                )
        from dataclasses import replace
        return replace(role, updated_at=updated_at)

    def delete_role(self, role_id: str) -> bool:
        """Soft-delete a role. Raises if it has child roles."""
        with self._session() as session:
            row = session.get(_RoleRow, role_id)
            if row is None:
                raise RoleNotFound(f"Role {role_id} not found")
            # Check for children
            child_stmt = select(_RoleRow.id).where(
                _RoleRow.parent_id == role_id,
                _RoleRow.status != EntityStatus.DELETED.value,
            )
            children = session.scalars(child_stmt).first()
            if children:
                raise StorageError(
                    f"Cannot delete role {role_id}: it has child roles"
                )
            row.status = EntityStatus.DELETED.value
            row.updated_at = _utcnow()
            session.execute(
                delete(_RoleAssignmentRow).where(
                    _RoleAssignmentRow.role_id == role_id
                )
            )
        return True

    def list_roles(
        self,
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Role]:
        """List active roles, optionally filtered by domain."""
        with self._session() as session:
            stmt = select(_RoleRow).where(
                _RoleRow.status != EntityStatus.DELETED.value
            )
            if domain is not None:
                stmt = stmt.where(_RoleRow.domain == domain)
            stmt = stmt.offset(offset).limit(limit)
            rows = session.scalars(stmt).all()
            result = []
            for row in rows:
                perms = self._load_role_permissions(session, row.id)
                result.append(_row_to_role(row, perms))
        return result

    # ------------------------------------------------------------------
    # Permission operations
    # ------------------------------------------------------------------

    def create_permission(self, permission: Permission) -> Permission:
        """Create a new permission."""
        self._validate_permission(permission)
        with self._session() as session:
            if session.get(_PermissionRow, permission.id) is not None:
                raise DuplicateEntityError(
                    f"Permission {permission.id} already exists"
                )
            session.add(_permission_to_row(permission))
        return permission

    def get_permission(self, permission_id: str) -> Permission:
        """Retrieve a permission by ID."""
        with self._session() as session:
            row = session.get(_PermissionRow, permission_id)
        if row is None:
            raise PermissionNotFound(f"Permission {permission_id} not found")
        return _row_to_permission(row)

    def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission and remove it from all roles."""
        with self._session() as session:
            row = session.get(_PermissionRow, permission_id)
            if row is None:
                raise PermissionNotFound(
                    f"Permission {permission_id} not found"
                )
            session.execute(
                delete(_role_permissions).where(
                    _role_permissions.c.permission_id == permission_id
                )
            )
            session.delete(row)
        return True

    def list_permissions(
        self,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Permission]:
        """List permissions with optional resource_type filter."""
        with self._session() as session:
            stmt = select(_PermissionRow)
            if resource_type:
                stmt = stmt.where(
                    _PermissionRow.resource_type == resource_type
                )
            stmt = stmt.offset(offset).limit(limit)
            rows = session.scalars(stmt).all()
        return [_row_to_permission(r) for r in rows]

    # ------------------------------------------------------------------
    # Resource operations
    # ------------------------------------------------------------------

    def create_resource(self, resource: Resource) -> Resource:
        """Create a new resource."""
        self._validate_resource(resource)
        with self._session() as session:
            if session.get(_ResourceRow, resource.id) is not None:
                raise DuplicateEntityError(
                    f"Resource {resource.id} already exists"
                )
            session.add(_resource_to_row(resource))
        return resource

    def get_resource(self, resource_id: str) -> Resource:
        """Retrieve a resource by ID."""
        with self._session() as session:
            row = session.get(_ResourceRow, resource_id)
        if row is None or row.status == EntityStatus.DELETED.value:
            raise ResourceNotFound(f"Resource {resource_id} not found")
        return _row_to_resource(row)

    def delete_resource(self, resource_id: str) -> bool:
        """Soft-delete a resource."""
        with self._session() as session:
            row = session.get(_ResourceRow, resource_id)
            if row is None:
                raise ResourceNotFound(f"Resource {resource_id} not found")
            row.status = EntityStatus.DELETED.value
            row.updated_at = _utcnow()
        return True

    def list_resources(
        self,
        resource_type: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Resource]:
        """List active resources with optional filters."""
        with self._session() as session:
            stmt = select(_ResourceRow).where(
                _ResourceRow.status != EntityStatus.DELETED.value
            )
            if resource_type:
                stmt = stmt.where(_ResourceRow.type == resource_type)
            if domain is not None:
                stmt = stmt.where(_ResourceRow.domain == domain)
            stmt = stmt.offset(offset).limit(limit)
            rows = session.scalars(stmt).all()
        return [_row_to_resource(r) for r in rows]

    # ------------------------------------------------------------------
    # Role assignment operations
    # ------------------------------------------------------------------

    def assign_role(self, assignment: RoleAssignment) -> RoleAssignment:
        """Assign a role to a user."""
        self._validate_role_assignment(assignment)
        with self._session() as session:
            if session.get(_UserRow, assignment.user_id) is None:
                raise UserNotFound(f"User {assignment.user_id} not found")
            if session.get(_RoleRow, assignment.role_id) is None:
                raise RoleNotFound(f"Role {assignment.role_id} not found")
            pk = _assignment_pk(
                assignment.user_id, assignment.role_id, assignment.domain
            )
            if session.get(_RoleAssignmentRow, pk) is not None:
                raise DuplicateEntityError(
                    f"User {assignment.user_id} already has role "
                    f"{assignment.role_id} in domain {assignment.domain}"
                )
            session.add(_assignment_to_row(assignment))
        return assignment

    def revoke_role(
        self,
        user_id: str,
        role_id: str,
        domain: Optional[str] = None,
    ) -> bool:
        """Revoke a role from a user. Returns True if an assignment was removed."""
        with self._session() as session:
            pk = _assignment_pk(user_id, role_id, domain)
            row = session.get(_RoleAssignmentRow, pk)
            if row is None:
                return False
            session.delete(row)
        return True

    def get_user_roles(
        self,
        user_id: str,
        domain: Optional[str] = None,
    ) -> List[Role]:
        """Get all active (non-expired) roles assigned to a user."""
        with self._session() as session:
            if session.get(_UserRow, user_id) is None:
                raise UserNotFound(f"User {user_id} not found")
            now = _utcnow()
            stmt = select(_RoleAssignmentRow).where(
                _RoleAssignmentRow.user_id == user_id
            )
            if domain is not None:
                stmt = stmt.where(_RoleAssignmentRow.domain == domain)
            assignments = session.scalars(stmt).all()

            role_ids = {
                a.role_id
                for a in assignments
                if a.expires_at is None
                or _ensure_utc(a.expires_at) > now
            }

            roles = []
            for role_id in role_ids:
                role_row = session.get(_RoleRow, role_id)
                if role_row and role_row.status != EntityStatus.DELETED.value:
                    perms = self._load_role_permissions(session, role_id)
                    roles.append(_row_to_role(role_row, perms))
        return roles

    def get_role_users(
        self,
        role_id: str,
        domain: Optional[str] = None,
    ) -> List[User]:
        """Get all users that currently hold a specific role."""
        with self._session() as session:
            if session.get(_RoleRow, role_id) is None:
                raise RoleNotFound(f"Role {role_id} not found")
            now = _utcnow()
            stmt = select(_RoleAssignmentRow).where(
                _RoleAssignmentRow.role_id == role_id
            )
            if domain is not None:
                stmt = stmt.where(_RoleAssignmentRow.domain == domain)
            assignments = session.scalars(stmt).all()

            user_ids = {
                a.user_id
                for a in assignments
                if a.expires_at is None
                or _ensure_utc(a.expires_at) > now
            }

            users = []
            for uid in user_ids:
                user_row = session.get(_UserRow, uid)
                if user_row and user_row.status != EntityStatus.DELETED.value:
                    users.append(_row_to_user(user_row))
        return users

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, int]:
        """Return counts of active entities in each table."""
        with self._session() as session:
            def count(model, status_col=None):
                stmt = select(model)
                if status_col is not None:
                    stmt = stmt.where(
                        status_col != EntityStatus.DELETED.value
                    )
                return len(session.scalars(stmt).all())

            return {
                "users": count(_UserRow, _UserRow.status),
                "roles": count(_RoleRow, _RoleRow.status),
                "permissions": count(_PermissionRow),
                "resources": count(_ResourceRow, _ResourceRow.status),
                "role_assignments": count(_RoleAssignmentRow),
            }

    def clear_all(self) -> None:
        """Delete all rows from all RBAC tables. Useful for test teardown."""
        with self._session() as session:
            for tbl in reversed(_Base.metadata.sorted_tables):
                session.execute(tbl.delete())
        logger.debug("SQLAlchemyStorage: all tables cleared")
