from flask import Flask
import os
import psycopg2
from psycopg2 import pool

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

    return app
