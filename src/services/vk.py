from http import HTTPStatus

import requests
from flask import redirect

from core.config import (
    VK_API_URL,
    VK_API_VERSION,
    VK_AUTHORIZE_PARAMS,
    VK_AUTHORIZE_URL,
    VK_CLIENT_ID,
    VK_CLIENT_SECRET,
    VK_GET_ACCESS_TOKEN_URL,
    VK_REDIRECT_URI,
)

from .help_functions import register_new_user
from .oauth_base import OauthService
from .oauth_client import OauthClient

client_vk = OauthClient(
    "VK",
    VK_CLIENT_ID,
    app_redirect_url=VK_REDIRECT_URI,
    permissions=["email", "photos"],
    api_v=VK_API_VERSION,
    security_code=VK_CLIENT_SECRET,
)


def get_user_info_from_vk_api(response, client: OauthClient) -> str:
    """Функция получения доп информации о пользователе от ответа VK"""
    data = response.json()
    client.access_token = data["access_token"]
    client.email = data["email"]
    client.user_id = data["user_id"]
    client.expires_in = data["expires_in"]

    redirect_url = VK_API_URL

    data = {
        "user_ids": client.user_id,
        "fields": "bdate",
        "access_token": client.access_token,
        "v": client.api_v,
    }
    response = requests.post(redirect_url, data=data)
    response_data = response.json()["response"][0]
    client.first_name = response_data.get("first_name")
    client.last_name = response_data.get("last_name")
    client.bdate = response_data.get("bdate")

    return str(client)


class OauthVkService(OauthService):
    def get_code(self, code):

        if code:
            client_vk.code = code
            data = {
                "client_id": client_vk.app_id,
                "client_secret": client_vk.security_code,
                "display": "page",
                "redirect_uri": client_vk.app_redirect_url,
                "code": client_vk.code,
            }
            redirect_url = VK_GET_ACCESS_TOKEN_URL
            response = requests.post(redirect_url, data=data)
            user_info = get_user_info_from_vk_api(response, client_vk)
            try:
                login, password = register_new_user(client_vk)
                return f"user {login} created with password {password}, user_info: {user_info}"

            except BaseException as e:
                return str(e), HTTPStatus.BAD_REQUEST

    def redirect_to_oauth(self):
        client_id = client_vk.app_id
        display = "page"
        redirect_uri = client_vk.app_redirect_url
        scope = " ".join(client_vk.permissions)
        response_type = "code"
        v = client_vk.api_v

        params = VK_AUTHORIZE_PARAMS.format(
            client_id, display, redirect_uri, scope, response_type, v
        )
        redirect_url = VK_AUTHORIZE_URL + "?" + params

        return redirect(redirect_url)
