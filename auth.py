from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    logout_user,
)
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from .user import User
import psycopg2
from psycopg2 import pool
import os

auth = Blueprint("auth", __name__)

POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
pool = pool.SimpleConnectionPool(1, 20, POSTGRESQL_URL)


def get_user_id(conn, email):
    with conn.cursor() as cursor:
        cursor.execute(
            "select id,password from users where email = %(email)s",
            {"email": email},
        )
        user_id = cursor.fetchone()
    return user_id


def get_user(conn, email) -> User:
    return User(email)


def check_password(conn, email, password) -> bool:
    with conn.cursor() as cursor:
        cursor.execute(
            "select password from users where email = %(email)s",
            {"email": email},
        )
        hashed_password = cursor.fetchone()

    return check_password_hash(hashed_password, password)


@auth.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    # login code goes here
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    with pool.getconn() as conn:
        if not check_password(conn, email, password):
            flash("Please check your login details and try again.")
            return redirect(url_for("auth.login"))

        user = get_user(conn, email)
    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for("main.profile"))


@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@auth.route("/signup")
def signup():
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get("email")
    password = request.form.get("password")

    with pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "select user from users where email = %(email)s",
                {"email": email},
            )
            user = cursor.fetchone()

    if (
        user
    ):  # if a user is found, we want to redirect back to signup page so user can try again
        flash("Email address already exists")
        return redirect(url_for("auth.login"))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    password = generate_password_hash(password)

    # add the new user to the database

    with pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "insert into users (email,password) values (%(email)s,%(password)s)",
                {"email": email, "password": password},
            )

    return redirect(url_for("auth.login"))
