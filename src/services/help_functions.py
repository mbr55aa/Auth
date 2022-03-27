import datetime
import random
import string
import uuid
from typing import Tuple

from werkzeug.security import generate_password_hash

from services.oauth_client import OauthClient
from db.db import db
from db.db_models import SocialAccount, User


def generate_random_string(length: int) -> str:
    """Функция генерации рэндомной строки длины length"""
    alphabet = string.ascii_letters + string.digits
    rand_string = "".join(random.choice(alphabet) for i in range(length))
    return rand_string


def gen_uniq_login() -> str:
    """Функция генерации уникального (не занятого) логина пользователя"""
    login = None
    login_uniq = False
    while not login_uniq:
        login = generate_random_string(8)
        user = User.query.filter_by(login=login).first()
        if not user:
            login_uniq = True
    return login


def gen_password():
    """Функция генерации пароля пользователя"""
    return generate_random_string(16)


def register_new_user(client: OauthClient) -> Tuple[str, str]:
    """Функция регистрации нового пользователя"""
    # Яндекс передает логин пользователя, если у нас пользователь с таким логином уже существует, то в дальнейшем
    # пользователю будет предложено самостоятельно ввести новый логин
    if not client.login:
        login = gen_uniq_login()
        client.login = login

    password = gen_password()
    client.pswd = password
    user = User.get_user_by_universal_login(client.login, client.email)
    if user:
        raise Exception("user with this email or login already exist")

    # Создаём нового пользователя
    create_user(client)
    # Пишем информацию о пользователе во вспомогательную таблицу
    add_row_to_social_account(client)
    return client.login, client.pswd


def get_user_id(client: OauthClient) -> uuid:
    """Функция получения идентификатора пользователя из БД"""
    user = User.query.filter_by(email=client.email).first()
    return user.id


def add_row_to_social_account(client: OauthClient) -> None:
    """Функция добавления во вспомогательную таблицу БД информации о пользователе"""
    social_account = SocialAccount(
        user_id=get_user_id(client),
        social_id=client.user_id,
        social_name=client.social_name,
    )
    db.session.add(social_account)
    db.session.commit()


def create_user(client: OauthClient) -> None:
    """Функция создания пользователя в БД"""
    user = User(
        login=client.login,
        email=client.email,
        password=generate_password_hash(client.pswd, method="sha256"),
        first_name=client.first_name,
        last_name=client.last_name,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.session.add(user)
    db.session.commit()
