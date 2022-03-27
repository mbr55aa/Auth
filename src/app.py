import datetime
from datetime import timedelta

import click
import uvicorn
from flasgger import Swagger, swag_from
from flask import Flask, request
from flask.cli import AppGroup
from flask_alembic import Alembic
from flask_jwt_extended import JWTManager
from flask_opentracing import FlaskTracer
from flask_restful import Api, Resource
from jaeger_client import Config
from werkzeug.security import generate_password_hash

from api.v1.auth import blueprint_auth
from api.v1.auth import limiter as auth_limiter
from api.v1.main import blueprint_main
from api.v1.main import limiter as main_limiter
from api.v1.oauth import blueprint_oauth
from api.v1.oauth import limiter as oauth_limiter
from api.v1.role import blueprint_role
from api.v1.role import limiter as role_limiter
from api.v1.user_role import blueprint_user_role
from api.v1.user_role import limiter as user_role_limiter
from core import config, rights
from db.db import db, init_db
from db.db_models import Role, User, UserRole

app = Flask(__name__)


@app.before_request
def before_request():
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        raise RuntimeError("request id is required")


jaeger_config = {
    "sampler": {
        "type": "const",
        "param": 1,
    },
    "local_agent": {
        "reporting_host": "jaeger",
        "reporting_port": "6831",
    },
    "logging": True,
}


def _setup_jaeger():
    _config = Config(
        config=jaeger_config,
        service_name="movies-api",
        validate=True,
    )
    return _config.initialize_tracer()


tracer = FlaskTracer(_setup_jaeger, app=app)


# Register limiters
auth_limiter.init_app(app)
main_limiter.init_app(app)
role_limiter.init_app(app)
user_role_limiter.init_app(app)
oauth_limiter.init_app(app)


swag = Swagger(app, template_file="api/v1/openapi/swagger.yaml", parse=True)

app.config["SECRET_KEY"] = config.APP_SECRET_KEY
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = config.JWT_REFRESH_TOKEN_EXPIRES
app.config["CUSTOM_LIMIT"] = config.CUSTOM_LIMIT

jwt = JWTManager(app)

app.register_blueprint(blueprint_auth)
app.register_blueprint(blueprint_oauth)
app.register_blueprint(blueprint_role)
app.register_blueprint(blueprint_user_role)
app.register_blueprint(blueprint_main)


# Подготавливаем контекст и создаём таблицы
alembic = Alembic()
alembic.init_app(app)
init_db(app)
app.app_context().push()
alembic.revision("made changes")
alembic.upgrade()

user_cli = AppGroup("user")


# cli command example: `flask user create admin admin@localhost 123`
@user_cli.command("create")
@click.argument("login")
@click.argument("email")
@click.argument("password")
def create_user(login, email, password):
    user = User.query.filter_by(login=login).first()
    if user:
        return click.echo("User with this name already exist!")
    user = User.query.filter_by(email=email).first()
    if user:
        return click.echo("User with this email already exist!")
    user = User(
        login=login,
        email=email,
        password=generate_password_hash(password, method="sha256"),
        first_name="",
        last_name="",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    db.session.add(user)
    db.session.commit()

    role = Role.query.filter_by(name="admin").first()
    if role:
        role.rights = list(rights.Rights.RIGHTS)
    else:
        role = Role(
            name="admin", description="Administrator", rights=list(rights.Rights.RIGHTS)
        )
        db.session.add(role)
    db.session.commit()
    db.session.flush()

    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()


app.cli.add_command(user_cli)


def main():
    app.run(debug=True, host="0.0.0.0")


if __name__ == "__main__":
    # uvicorn.run(
    #     "app:app",
    #     host="127.0.0.1",
    #     port=5000,
    # )
    main()
