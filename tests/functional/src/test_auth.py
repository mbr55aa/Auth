from http import HTTPStatus

import pytest
import requests

from .db_models import User

user_payload = {
    "login": "app_test_user",
    "email": "gui@mitsuaki.com",
    "password": "pass_w0rd",
    "password_again": "pass_w0rd",
    "first_name": "Gui",
    "last_name": "Mitsuaki",
}


def test_user_sign_up(db_session, get_url):
    user = db_session.query(User).filter_by(login=user_payload["login"]).first()
    if user:
        db_session.delete(user)
        db_session.commit()

    response = requests.post(get_url + "/auth/sign_up", data=user_payload)
    assert response.status_code == HTTPStatus.CREATED
    user = db_session.query(User).filter_by(login=user_payload["login"]).first()
    assert user
    assert user.email == user_payload["email"]


def test_user_sign_up_with_used_login(get_url):
    double_user = user_payload.copy()
    double_user["email"] = "test@test.com"
    response = requests.post(get_url + "/auth/sign_up", data=double_user)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json().get("error") == "This login is already being used"


def test_user_sign_up_with_used_email(get_url):
    double_user = user_payload.copy()
    double_user["login"] = "test"
    response = requests.post(get_url + "/auth/sign_up", data=double_user)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json().get("error") == "This email address is already being used"


def test_user_sign_up_password_not_match(get_url):
    double_user = user_payload.copy()
    double_user["email"] = "test@test.com"
    double_user["login"] = "test"
    double_user["password_again"] = "not_the_same_password"

    response = requests.post(get_url + "/auth/sign_up", data=double_user)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json().get("error") == "Passwords do not match"


def test_user_sign_in(get_url):
    response = requests.post(
        get_url + "/auth/sign_in",
        data={"login": user_payload["login"], "password": user_payload["password"]},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json().get("access_token")
    assert response.json().get("refresh_token")


def test_user_delete(db_session):
    user = db_session.query(User).filter_by(login=user_payload["login"]).first()
    assert user

    db_session.delete(user)
    db_session.commit()

    user = db_session.query(User).filter_by(login=user_payload["login"]).first()
    assert user is None
