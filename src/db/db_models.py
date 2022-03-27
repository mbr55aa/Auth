import uuid
from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, event, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.ddl import DDL

from db.db import db


class UsersMixin:
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    first_name = db.Column(db.String(1000), nullable=False)
    last_name = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)


class User(UsersMixin, UserMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('id', 'created_at'),
        {
            'postgresql_partition_by': 'RANGE (created_at)',
        }
    )

    role = db.relationship(
        "UserRole",
        backref=db.backref("users", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    @classmethod
    def get_user_by_universal_login(cls, login: Optional[str] = None, email: Optional[str] = None):
        return cls.query.filter(or_(cls.login == login, cls.email == email)).first()

    def __repr__(self):
        return f"<User {self.login}>"


class User2022(UsersMixin, UserMixin, db.Model):
    __tablename__ = 'users2022'


class User2023(UsersMixin, UserMixin, db.Model):
    __tablename__ = 'users2023'


User2022.__table__.add_is_dependent_on(User.__table__)
User2023.__table__.add_is_dependent_on(User.__table__)
event.listen(
    User2022.__table__,
    "after_create",
    DDL("""ALTER TABLE users ATTACH PARTITION users2022 FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');""")
)
event.listen(
    User2023.__table__,
    "after_create",
    DDL("""ALTER TABLE users ATTACH PARTITION users2023 FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');""")
)


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    rights = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)

    user = db.relationship(
        "UserRole",
        backref=db.backref("role", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Role {self.description}>"


class UserRole(db.Model):
    __tablename__ = "user_role"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("users.id"))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey("role.id"))

    def __repr__(self):
        return f"<user {self.user_id} has role {self.role_id}>"


class UserLoginsMixin:

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    time = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    browser = db.Column(db.String, unique=True, nullable=False)
    platform = db.Column(db.String, unique=True, nullable=False)
    ip = db.Column(db.String, unique=True, nullable=False)


class UserLogins(UserLoginsMixin, db.Model):
    __tablename__ = "user_logins"
    __table_args__ = (
        UniqueConstraint('id', 'time'),
        {
            'postgresql_partition_by': 'RANGE (time)',
        }
    )

    def __repr__(self):
        return f"<user {self.user_id} last login {self.time}>"


class UserLogins2022(UserLoginsMixin, db.Model):
    __tablename__ = 'user_logins_2022'


class UserLogins2023(UserLoginsMixin, db.Model):
    __tablename__ = 'user_logins_2023'


UserLogins2022.__table__.add_is_dependent_on(UserLogins.__table__)
UserLogins2023.__table__.add_is_dependent_on(UserLogins.__table__)
event.listen(
    UserLogins2022.__table__,
    "after_create",
    DDL("""ALTER TABLE users ATTACH PARTITION user_logins_2022 FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');""")
)
event.listen(
    UserLogins2023.__table__,
    "after_create",
    DDL("""ALTER TABLE users ATTACH PARTITION user_logins_2023 FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');""")
)


class SocialAccount(db.Model):
    __tablename__ = 'social_account'

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'),)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'