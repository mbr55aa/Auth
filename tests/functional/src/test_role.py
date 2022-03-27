from http import HTTPStatus

import pytest
import requests

from .db_models import Role, User, UserRole

role_payload = {
    "name": "test_role",
    "description": "Role for tests",
    "rights": '["create_users", "create_roles", "update_roles"]',
}

user_payload = {
    "login": "pamela_hering",
    "email": "pamela@hering.com",
    "password": "some_hash",
    "first_name": "Pamela",
    "last_name": "Hering",
}


def test_create_role(superuser_token, db_session, get_url):
    role = db_session.query(Role).filter_by(name=role_payload["name"]).first()
    if role:
        db_session.delete(role)
        db_session.commit()

    headers = {"Authorization": f"Bearer {superuser_token}"}

    response = requests.post(get_url + "/role/", headers=headers, data=role_payload)
    assert response.status_code == HTTPStatus.CREATED


def test_list_role(superuser_token, db_session, get_url):
    role = db_session.query(Role).all()

    headers = {"Authorization": f"Bearer {superuser_token}"}

    response = requests.get(get_url + "/role/", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == len(role)


def test_grant_role(superuser_token, get_or_create, db_session, get_url):
    user, _ = get_or_create(User, **user_payload)
    role, _ = get_or_create(
        Role, name=role_payload["name"], description=role_payload["description"]
    )

    headers = {"Authorization": f"Bearer {superuser_token}"}

    # Add role to user
    response = requests.post(
        get_url + "/user_role/" + str(user.id),
        headers=headers,
        data={"role_id": role.id},
    )
    assert response.status_code == HTTPStatus.OK

    db_session.query(UserRole).filter_by(user_id=user.id).delete()
    db_session.delete(user)
    db_session.delete(role)
    db_session.commit()


def test_revoke_role(superuser_token, get_or_create, db_session, get_url):
    user, _ = get_or_create(User, **user_payload)
    role, _ = get_or_create(
        Role, name=role_payload["name"], description=role_payload["description"]
    )
    user_role, _ = get_or_create(UserRole, user_id=user.id, role_id=role.id)

    headers = {"Authorization": f"Bearer {superuser_token}"}

    # Revoke role
    response = requests.delete(
        get_url + "/user_role/" + str(user.id),
        headers=headers,
        data={"role_id": role.id},
    )
    assert response.status_code == HTTPStatus.OK

    user_roles = db_session.query(UserRole).filter_by(user_id=user.id).all()
    assert not user_roles

    db_session.delete(user)
    db_session.delete(role)
    db_session.commit()
