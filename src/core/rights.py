from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps
from http import HTTPStatus

from db.db import db
from db.db_models import Role, UserRole


class Rights:
    CREATE_USERS = 'create_users'
    READ_USERS = 'read_users'
    UPDATE_USERS = 'update_users'
    DELETE_USERS = 'delete_users'
    CREATE_ROLES = 'create_roles'
    READ_ROLES = 'read_roles'
    UPDATE_ROLES = 'update_roles'
    DELETE_ROLES = 'delete_roles'

    RIGHTS = {
        CREATE_USERS: 'Allow Create Users',
        READ_USERS: 'Allow Read Users',
        UPDATE_USERS: 'Allow Update Users',
        DELETE_USERS: 'Allow Delete Users',
        CREATE_ROLES: 'Allow Create Roles',
        READ_ROLES: 'Allow Read Roles',
        UPDATE_ROLES: 'Allow Update Roles',
        DELETE_ROLES: 'Allow Delete Roles',
    }


def get_rights(user_id):
    rights = db.session.query(Role.rights).filter(UserRole.user_id == user_id).filter(Role.id == UserRole.role_id).all()
    rights_set = set()
    for r in rights:
        rights_set.update(r[0])
    return rights_set


def check_rights(access_right):
    def func_wrapper(func):
        @wraps(func)
        @jwt_required()
        def inner(*args, **kwargs):
            current_user = get_jwt_identity()
            if access_right not in get_rights(current_user):
                return jsonify({"error": "Not allowed"}), HTTPStatus.FORBIDDEN
            return func(*args, **kwargs)
        return inner
    return func_wrapper
