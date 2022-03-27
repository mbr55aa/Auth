from http import HTTPStatus

import requests
from flask import Blueprint, jsonify, redirect, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from services.vk import OauthVkService
from services.yandex import OauthYandexService

limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)

blueprint_oauth = Blueprint(name="oauth", url_prefix="/oauth", import_name=__name__)
oauth_limit = limiter.shared_limit("100/hour", scope="oauth")


@blueprint_oauth.route("/<string:provider_name>", methods=["POST", "GET"])
@oauth_limit
def oauth_login(provider_name):
    if provider_name == "vk":
        service = OauthVkService()
    elif provider_name == "yandex":
        service = OauthYandexService()
    else:
        return jsonify({"error": "Oauth service not found"}), HTTPStatus.NOT_FOUND

    code = request.args.get("code")
    if code:
        return service.get_code(code)
    else:
        return service.redirect_to_oauth()
