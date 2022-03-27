import os

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    postgres_host: str = Field("127.0.0.1", env="POSTGRES_HOST")
    postgres_port: str = Field(5432, env="POSTGRES_PORT")
    postgres_user: str = Field("postgres", env="POSTGRES_USER")
    postgres_password: str = Field("Passw0rd", env="POSTGRES_PASSWORD")
    postgres_db: str = Field("auth", env="POSTGRES_DB")

    redis_host: str = Field("127.0.0.1", env="REDIS_HOST")
    redis_port: str = Field(6379, env="REDIS_PORT")

    service_url = "http://localhost:5000"
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
