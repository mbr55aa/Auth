# flask_app/db.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from core import config

db = SQLAlchemy()


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}/{config.POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def init_db(app: Flask):
    app.config.from_object(Config())
    db.init_app(app)
