from http import HTTPStatus

from flask import Blueprint, g, jsonify, render_template, request
from flask_jwt_extended import get_jwt, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from api.v1.auth import verify_access_token
from db.db_models import User

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

blueprint_main = Blueprint("main", __name__)
main_limit = limiter.shared_limit("1000/day;100/hour;10/minute", scope="main")


@blueprint_main.route("/")
@main_limit
def index():
    return render_template("index.html")


@blueprint_main.route("/profile")
@main_limit
@jwt_required()
def profile():
    access_token_payload = get_jwt()

    answer = verify_access_token(access_token_payload)
    if answer:
        return jsonify({"error": answer}), HTTPStatus.BAD_REQUEST

    user_id = access_token_payload["sub"]
    user = User.query.get(user_id)
    g.user = user
    return render_template("profile.html")
