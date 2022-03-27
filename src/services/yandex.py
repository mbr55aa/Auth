from http import HTTPStatus

import requests
from flask import redirect

from core.config import (
    YANDEX_API_URL,
    YANDEX_AUTHORIZE_PARAMS,
    YANDEX_AUTHORIZE_URL,
    YANDEX_CALLBACK_URL,
    YANDEX_CLIENT_ID,
    YANDEX_CLIENT_SECRET,
    YANDEX_GET_ACCESS_TOKEN_URL,
)

from .help_functions import register_new_user
from .oauth_base import OauthService
from .oauth_client import OauthClient

client_yandex = OauthClient(
    "yandex",
    YANDEX_CLIENT_ID,
    app_redirect_url=YANDEX_CALLBACK_URL,
    security_code=YANDEX_CLIENT_SECRET,
)


def get_user_info_from_yandex_api(response, client: OauthClient) -> str:
    """Функция получения доп информации о пользователе от ответа VK"""
    data = response.json()
    client.access_token = data["access_token"]
    client.expires_in = data["expires_in"]

    redirect_url = YANDEX_API_URL

    data = {
        "oauth_token": client.access_token,
    }

    response = requests.post(redirect_url, data=data)
    response_data = response.json()
    client.login = response_data["login"]
    client.user_id = response_data["client_id"]
    client.first_name = response_data.get("first_name")
    client.last_name = response_data.get("last_name")
    client.email = response_data.get("default_email")
    client.bdate = response_data.get("birthday")

    return str(client)


class OauthYandexService(OauthService):
    def get_code(self, code):
        if code:
            client_yandex.code = code
            data = {
                "grant_type": "authorization_code",
                "client_id": client_yandex.app_id,
                "client_secret": client_yandex.security_code,
                "code": client_yandex.code,
            }
            redirect_url = YANDEX_GET_ACCESS_TOKEN_URL
            response = requests.post(redirect_url, data=data)
            user_info = get_user_info_from_yandex_api(response, client_yandex)
            try:
                login, password = register_new_user(client_yandex)
                return f"user {login} created with password {password}, user_info: {user_info}"

            except BaseException as e:
                return str(e), HTTPStatus.BAD_REQUEST

    def redirect_to_oauth(self):
        client_id = client_yandex.app_id
        display = "popup"
        redirect_uri = client_yandex.app_redirect_url
        response_type = "code"

        params = YANDEX_AUTHORIZE_PARAMS.format(
            client_id, display, redirect_uri, response_type
        )
        redirect_url = YANDEX_AUTHORIZE_URL + "?" + params

        return redirect(redirect_url)
