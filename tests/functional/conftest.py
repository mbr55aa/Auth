import json
from http import HTTPStatus

import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .settings import Settings
from .src.db_models import Role, User, UserRole

settings = Settings()
SERVICE_URL = settings.service_url
SUPERUSER_ROLE = "superuser"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )
    return engine


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    session = Session(bind=connection)
    yield session
    session.close()


@pytest.fixture(scope="function")
def get_url():
    return SERVICE_URL


@pytest.fixture
def get_or_create(db_session):
    def inner(model, defaults=None, **kwargs):
        instance = db_session.query(model).filter_by(**kwargs).one_or_none()
        if instance:
            return instance, False
        else:
            kwargs |= defaults or {}
            instance = model(**kwargs)
            try:
                db_session.add(instance)
                db_session.commit()
            except Exception:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
                db_session.rollback()
                instance = db_session.query(model).filter_by(**kwargs).one()
                return instance, False
            else:
                return instance, True

    return inner


@pytest.fixture(scope="function")
def superuser_token(get_or_create, db_session, get_url):
    # user_payload = {
    #     "login": "app_test_user",
    #     "email": "gui@mitsuaki.com",
    #     "password": "pass_w0rd",
    #     "password_again": "pass_w0rd",
    #     "first_name": "Gui",
    #     "last_name": "Mitsuaki",
    # }
    #
    # superuser = db_session.query(User).filter_by(login=user_payload["login"]).first()
    # if not superuser:
    #     response = requests.post(get_url + "/auth/sign_up", data=user_payload)
    #     assert response.status_code == HTTPStatus.CREATED
    #     superuser = (
    #         db_session.query(User).filter_by(login=user_payload["login"]).first()
    #     )
    # role, _ = get_or_create(Role, name=SUPERUSER_ROLE, description="")
    # user_role, _ = get_or_create(UserRole, user_id=superuser.id, role_id=role.id)

    user_payload = {
        "login": "admin",
        "password": "123",
    }

    response = requests.post(
        get_url + "/auth/sign_in",
        data={"login": user_payload["login"], "password": user_payload["password"]},
    )
    assert response.status_code == HTTPStatus.OK
    access_token = response.json().get("access_token")
    assert access_token

    yield access_token

    # db_session.delete(user_role)
    # db_session.delete(superuser)
    # db_session.commit()
