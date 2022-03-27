import os
from datetime import timedelta

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "AuthService")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Настройки Postgres
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Passw0rd")
POSTGRES_DB = os.getenv("POSTGRES_DB", "auth")

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "9OLWxND4o83j4K4iuopO")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hbjd4hrbh2j3ber324j3")

# Время жизни jwt токенов
JWT_ACCESS_TOKEN_EXPIRES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=1))
JWT_REFRESH_TOKEN_EXPIRES = os.getenv("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30))

CUSTOM_LIMIT = os.getenv("CUSTOM_LIMIT", "10/s")

VK_CLIENT_ID = os.getenv("VK_CLIENT_ID", "")
VK_CLIENT_SECRET = os.getenv("VK_CLIENT_SECRET", "")
VK_API_VERSION = os.getenv("VK_API_VERSION", "")
VK_REDIRECT_URI = os.getenv("VK_REDIRECT_URI", "")
VK_GET_ACCESS_TOKEN_URL = os.getenv(
    "VK_GET_ACCESS_TOKEN_URL", "https://oauth.vk.com/access_token/"
)
VK_AUTHORIZE_URL = os.getenv("VK_AUTHORIZE_URL", "https://oauth.vk.com/authorize")
VK_AUTHORIZE_PARAMS = os.getenv(
    "VK_AUTHORIZE_PARAMS",
    "client_id={}&display={}&redirect_uri={}&scope={}&response_type={}&v={}",
)
VK_API_URL = os.getenv("VK_API_URL", "https://api.vk.com/method/users.get")


YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID", "")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET", "")
YANDEX_CALLBACK_URL = os.getenv("YANDEX_CALLBACK_URL", "")
YANDEX_GET_ACCESS_TOKEN_URL = os.getenv(
    "YANDEX_GET_ACCESS_TOKEN_URL", "https://oauth.yandex.ru/token"
)
YANDEX_AUTHORIZE_URL = os.getenv(
    "YANDEX_AUTHORIZE_URL", "https://oauth.yandex.ru/authorize"
)
YANDEX_AUTHORIZE_PARAMS = os.getenv(
    "YANDEX_AUTHORIZE_PARAMS",
    "client_id={}&display={}&redirect_uri={}&response_type={}",
)
YANDEX_API_URL = os.getenv("YANDEX_API_URL", "https://login.yandex.ru/info")
