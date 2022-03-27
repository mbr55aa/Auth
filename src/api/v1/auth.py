import base64
import datetime
import json
import uuid
from http import HTTPStatus
from typing import Optional, Tuple

from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash, generate_password_hash

from core import config
from core.rights import Rights, get_rights
from db.db import db
from db.db_models import User
from db.redis import redis_db

from .protobuf import user_pb2

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

blueprint_auth = Blueprint(name="auth", url_prefix="/auth", import_name=__name__)
auth_limit = limiter.shared_limit("100/hour", scope="auth")


def get_token_payload_data(token: str, claim: str) -> str:
    """Функция для получения содержимого полей из полезной нагрузки токена"""
    payload = token.split('.')[1]
    decode_payload = base64.urlsafe_b64decode(payload + '=' * (4 - len(payload) % 4))
    payload_dict = json.loads(decode_payload.decode('utf-8'))
    return payload_dict.get(claim)


def create_tokens(identity: uuid) -> Tuple[str, str]:
    """Функция создания access и refresh токенов"""
    refresh_token = create_refresh_token(identity=identity)
    refresh_token_id = get_token_payload_data(refresh_token, 'jti')
    print(refresh_token_id)
    additional_claims = {"rti": f"{refresh_token_id}"}
    access_token = create_access_token(identity=identity, fresh=True, additional_claims=additional_claims)
    return access_token, refresh_token


def get_timedelta_token_exp_now(token_payload: dict):
    """Функция, вовращающая количество секунд, в течении которых токен еще жив"""
    token_exp_unix = token_payload['exp']
    token_exp_dt = datetime.datetime.fromtimestamp(int(token_exp_unix))
    dt_now = datetime.datetime.now()
    timedelta = (token_exp_dt - dt_now).total_seconds()
    return timedelta


def put_token_to_redis(token: str) -> None:
    """Функция, записывающая токен в БД Redis"""
    token_id = get_token_payload_data(token, 'jti')
    token_type = get_token_payload_data(token, 'type')
    if token_type == 'refresh':
        ttl = config.JWT_REFRESH_TOKEN_EXPIRES
    elif token_type == 'access':
        ttl = config.JWT_ACCESS_TOKEN_EXPIRES
    redis_db.setex(f'{token_type}.{token_id}', ttl, 'ok')


def del_token_from_redis(token: str) -> None:
    """Функция удаления токена из БД Redis"""
    token_id = get_token_payload_data(token, 'jti')
    token_type = get_token_payload_data(token, 'type')
    redis_db.delete(f'{token_type}.{token_id}')


def verify_access_token(access_token_payload: dict) -> Optional[str]:
    """Функция проверки access токена"""
    # Проверяем что access токен не просрочен
    ttl = get_timedelta_token_exp_now(access_token_payload)
    if ttl < 0:
        return "token is overdue"

    # Проверяем что access токен не отозван
    if redis_db.get(f"access.{access_token_payload['jti']}"):
        return "access token is revoked"

    # TODO Добавить проверку подписи токена
    return None


@blueprint_auth.route("/sign_up")
@auth_limit
def sign_up():
    return render_template("auth/signup.html")


@blueprint_auth.route("/sign_up", methods=["POST"])
@auth_limit
def sign_up_post():
    login = request.form.get("login")
    email = request.form.get("email")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    password = request.form.get("password")
    password_again = request.form.get("password_again")
    created_at = datetime.datetime.now()
    updated_at = datetime.datetime.now()

    user = User.query.filter_by(login=login).first()

    if user:
        return (
            jsonify({"error": "This login is already being used"}),
            HTTPStatus.BAD_REQUEST,
        )
    # Возможно следует убрать эту проверу на уровень формы
    if password_again != password:
        return jsonify({"error": "Passwords do not match"}), HTTPStatus.BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if user:
        return (
            jsonify({"error": "This email address is already being used"}),
            HTTPStatus.BAD_REQUEST,
        )

    new_user = User(
        login=login,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=generate_password_hash(password, method="sha256"),
        created_at=created_at,
        updated_at=updated_at,
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"status": "Successfully created"}), HTTPStatus.CREATED


@blueprint_auth.get("/sign_in")
@auth_limit
def sign_in():
    return render_template("auth/signin.html")


@blueprint_auth.route("/sign_in", methods=["POST"])
@auth_limit
def sign_in_post():
    login = request.form.get("login")
    password = request.form.get("password")

    user = User.query.filter_by(login=login).first()

    if not user:
        user = User.query.filter_by(email=login).first()

    if not user:
        return (
            jsonify({"error": "There is no user with that login"}),
            HTTPStatus.BAD_REQUEST,
        )

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect Password"}), HTTPStatus.BAD_REQUEST

    access_token, refresh_token = create_tokens(user.id)
    put_token_to_redis(refresh_token)

    return jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK


@blueprint_auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    access_token_payload = get_jwt()
    ttl = get_timedelta_token_exp_now(access_token_payload)
    if ttl > 0:
        # Кладем access токен в Redis - это будет означать что он стал не валидным
        redis_db.setex(f'{access_token_payload["type"]}.{access_token_payload["jti"]}', int(ttl), 'ok')
        redis_db.delete(f'refresh.{access_token_payload["rti"]}')

    return jsonify({"status": "Successfully logging out"}), HTTPStatus.OK


@blueprint_auth.route("/refresh_token", methods=["POST"])
@auth_limit
@jwt_required()
def refresh():
    access_token_payload = get_jwt()
    refresh_token = json.loads(request.data).get('refresh_token')

    if not refresh_token:
        return jsonify({"error": "no refresh token"}), HTTPStatus.BAD_REQUEST

    if redis_db.get(f"access.{access_token_payload['jti']}"):
        return jsonify({"error": "access token is revoked"}), HTTPStatus.BAD_REQUEST

    refresh_token_id = get_token_payload_data(refresh_token, 'jti')
    if not redis_db.get(f'refresh.{refresh_token_id}'):
        return jsonify({"error": "refresh token is revoked"}), HTTPStatus.BAD_REQUEST

    redis_db.delete(f'refresh.{refresh_token_id}')
    identity = get_jwt_identity()
    access_token, refresh_token = create_tokens(identity)

    return jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK


@blueprint_auth.route("/change_password", methods=["POST"])
@auth_limit
@jwt_required()
def change_password_post():
    access_token_payload = get_jwt()

    answer = verify_access_token(access_token_payload)
    if answer:
        return jsonify({"error": answer}), HTTPStatus.BAD_REQUEST

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")

    user_email = request.form.get("email")

    user = User.query.filter_by(email=user_email).first()

    if check_password_hash(user.password, old_password):
        user.password = generate_password_hash(new_password, method="sha256")
        db.session.commit()
        return jsonify({"status": "Successfully updated"}), HTTPStatus.OK
    else:
        return jsonify({"error": "Password not updated. Incorrect Password"}), HTTPStatus.BAD_REQUEST


@blueprint_auth.route("/profile", methods=["GET"])
@jwt_required()
@auth_limit
def get_user_info():
    current_user = get_jwt_identity()
    user = user_pb2.UserInfoReply(
        id=str(current_user.id),
        login=current_user.login,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        rights=get_rights(current_user.id)
    )
    return user.SerializeToString()


