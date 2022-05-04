from typing import Iterable
from flask import Flask, g
from flask_login import LoginManager
import os
import psycopg2
from psycopg2 import pool

# from psycopg2 import pool
from .user import User
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.shared_data import SharedDataMiddleware

POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
pool = pool.SimpleConnectionPool(1, 20, POSTGRESQL_URL)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["POSTGRESQL_URL"] = os.getenv("POSTGRESQL_URL")
    pool = psycopg2.pool.SimpleConnectionPool(1, 20, app.config["POSTGRESQL_URL"])

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        with pool.getconn() as conn:
            # since the user_id is just the primary key of our user table, use it in the query for the user
            return User.load_user(conn, int(user_id))

    @app.before_request
    def setup_db_connection():
        g.conn = pool.getconn()

    @app.after_request
    def close_db_connection(response):
        pool.putconn(g.conn)
        return response

    return app
