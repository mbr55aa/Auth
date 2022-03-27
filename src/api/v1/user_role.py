from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.rights import Rights, check_rights
from db.db import db
from db.db_models import UserRole

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

blueprint_user_role = Blueprint(name="user_role", url_prefix="/user_role", import_name=__name__)
user_role_limit = limiter.shared_limit("1000/day;100/hour;10/minute", scope="role")


@blueprint_user_role.route("/<user_id>", methods=["POST"])
@user_role_limit
@check_rights(Rights.UPDATE_USERS)
def grant_role(user_id):
    # Require `Authorization` in Headers with `Bearer <JWT>` value
    data = request.form
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        return jsonify({"error": "Wrong UUID"}), HTTPStatus.BAD_REQUEST
    try:
        role_uuid = UUID(data.get('role_id', ''), version=4)
    except ValueError:
        return jsonify({"error": "Wrong UUID"}), HTTPStatus.BAD_REQUEST
    user_role = UserRole.query.filter_by(user_id=user_uuid, role_id=role_uuid).first()
    if user_role:
        return jsonify({"error": "Already exists"}), HTTPStatus.NOT_ACCEPTABLE

    new_user_role = UserRole(user_id=user_uuid, role_id=role_uuid)
    db.session.add(new_user_role)
    db.session.commit()
    return jsonify({"status": "Successfully granted"}), HTTPStatus.OK


@blueprint_user_role.route("/<user_id>", methods=["DELETE"])
@user_role_limit
@check_rights(Rights.UPDATE_USERS)
def revoke_role(user_id):
    data = request.form
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        return jsonify({"error": "Wrong UUID"}), HTTPStatus.BAD_REQUEST
    try:
        role_uuid = UUID(data.get('role_id', ''), version=4)
    except ValueError:
        return jsonify({"error": "Wrong UUID"}), HTTPStatus.BAD_REQUEST
    user_role = UserRole.query.filter_by(user_id=user_uuid, role_id=role_uuid).first()
    if not user_role:
        return jsonify({"error": "Not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(user_role)
    db.session.commit()
    return jsonify({"status": "Successfully revoked"}), HTTPStatus.OK


@blueprint_user_role.route("/<user_id>", methods=["GET"])
@user_role_limit
@check_rights(Rights.READ_USERS)
def check_role(user_id):
    try:
        user_uuid = UUID(user_id, version=4)
    except ValueError:
        return jsonify({"error": "Wrong UUID"}), HTTPStatus.BAD_REQUEST

    user_roles = UserRole.query.filter_by(user_id=user_uuid).all()
    return jsonify([{"id": ur.id, "role_id": ur.role_id} for ur in user_roles or []])
