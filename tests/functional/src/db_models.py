import uuid
from datetime import datetime

from sqlalchemy import (JSON, TIMESTAMP, Column, ForeignKey, Integer, Sequence,
                        String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = Column(String, unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(1000), nullable=False)
    last_name = Column(String(1000), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    role = relationship(
        "UserRole",
        backref=backref("users", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class Role(Base):
    __tablename__ = "role"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    rights = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    user = relationship(
        "UserRole",
        backref=backref("role", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"))
