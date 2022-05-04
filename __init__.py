from flask import Flask
from flask_login import LoginManager
import os
import psycopg2
from psycopg2 import pool
from .user import User
from .auth import get_user

POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
pool = pool.SimpleConnectionPool(1, 20, POSTGRESQL_URL)


def create_app():
    global pool
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["POSTGRESQL_URL"] = POSTGRESQL_URL

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
        print("login")
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return get_user(int(user_id))

    return app
