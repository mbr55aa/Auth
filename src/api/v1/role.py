import json
from http import HTTPStatus
from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.rights import Rights, check_rights
from db.db import db
from db.db_models import Role

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

blueprint_role = Blueprint(name="role", url_prefix="/role", import_name=__name__)
role_limit = limiter.shared_limit("100/hour", scope="role")


@blueprint_role.route("/", methods=["POST"])
@role_limit
@check_rights(Rights.CREATE_ROLES)
def create_role():
    # Require `Authorization` in Headers with `Bearer <JWT>` value
    data = request.form
    name = data.get('name')
    rights = data.get('rights')  # string like ["create_users", "create_roles"]
    description = data.get('description', '')

    if not name or not rights:
        return jsonify({"error": "Lack of parameters"}), HTTPStatus.BAD_REQUEST
    role = Role.query.filter_by(name=name).first()
    if role:
        return jsonify({"error": "Already exists"}), HTTPStatus.NOT_ACCEPTABLE

    try:
        rights_set = set(json.loads(rights))
    except TypeError:
        return jsonify({"error": "Wrong Rights"}), HTTPStatus.BAD_REQUEST
    if not rights_set.issubset(set(Rights.RIGHTS)):
        return jsonify({"error": "Wrong Rights"}), HTTPStatus.BAD_REQUEST

    new_role = Role(name=name, description=description, rights=list(rights_set))
    db.session.add(new_role)
    db.session.commit()
    return jsonify({"status": "Successfully created"}), HTTPStatus.CREATED


@blueprint_role.route("/<role_id>", methods=["DELETE"])
@role_limit
@check_rights(Rights.DELETE_ROLES)
def delete_role(role_id):
    try:
        role_uuid = UUID(role_id, version=4)
    except ValueError:
        return jsonify({"error": "Wrong UUID"}), HTTPStatus.BAD_REQUEST
    role = Role.query.filter_by(id=role_uuid).first()
    if not role:
        return jsonify({"error": "Not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(role)
    db.session.commit()
    return jsonify({"status": "Successfully deleted"}), HTTPStatus.OK


@blueprint_role.route("/<role_id>", methods=["PATCH"])
@role_limit
@check_rights(Rights.UPDATE_ROLES)
def update_role(role_id):
    data = request.form

    try:
        role_uuid = UUID(role_id, version=4)
    except ValueError:
        return jsonify({"error": "Wrong UUID"}), HTTPStatus.BAD_REQUEST
    role = Role.query.filter_by(id=role_uuid).first()
    if not role:
        return jsonify({"error": "Not found"}), HTTPStatus.NOT_FOUND

    name = data.get('name')
    rights = data.get('rights')
    description = data.get('description')
    if not name and not rights and not description:
        return jsonify({"error": "Lack of parameters"}), HTTPStatus.BAD_REQUEST
    if name:
        # TODO добавить проверку что новое имя не занято
        role.name = name
    if rights:
        try:
            rights_set = set(json.loads(rights))
        except TypeError:
            return jsonify({"error": "Wrong Rights"}), HTTPStatus.BAD_REQUEST
        if not rights_set.issubset(set(Rights.RIGHTS)):
            return jsonify({"error": "Wrong Rights"}), HTTPStatus.BAD_REQUEST
        role.rights = list(rights_set)
    if description:
        role.description = description
    db.session.commit()
    return jsonify({"status": "Successfully updated"}), HTTPStatus.OK


@blueprint_role.route("/", methods=["GET"])
@role_limit
@check_rights(Rights.READ_ROLES)
def list_role():
    roles = Role.query.all()
    return jsonify([{"id": r.id, "name": r.name, "description": r.description} for r in roles or []]), HTTPStatus.OK
