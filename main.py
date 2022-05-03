from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    current_app,
)
import flask_login
import psycopg2
from psycopg2 import pool
import os
from .user import User

POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
pool = pool.SimpleConnectionPool(1, 20, POSTGRESQL_URL)

main = Blueprint("main", __name__)

# login_manager = flask_login.LoginManager()
# login_manager.init_app(main)


# @login_manager.user_loader
# def user_loader(name):
#     user = User(name)
#     if not user.is_authenticated:
#         return
#     return user


# @login_manager.unauthorized_handler
# def unauthorized_handler():
#     return "Unauthorized"


@main.route("/profile")
def profile():
    return render_template("profile.html")


def next_question(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            select question, id from questions limit 1
        """
        )
        question, question_id = cursor.fetchone()
        return question, question_id


@main.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")

    # if loggedin == True:
    #     if request.method == "POST":
    #         user_answer = request.form["answer"]
    #         new_question, next_id = next_question()
    #         question_id = request.form["question_id"]
    #         print("question_id", question_id)
    #         answer = get_answer(question_id)[0]
    #         result = answer == user_answer
    #         print("answer", answer)
    #         return render_template(
    #             "page.html",
    #             question=new_question,
    #             question_id=question_id,
    #             answer=answer,
    #             result=result,
    #         )
    #     else:
    #         question, question_id = next_question()
    #         return render_template(
    #             "page.html", question=question, question_id=question_id
    #         )
    # else:
    #     redirect(url_for(app.login))


def get_answer(question_id):
    with pool.getconn() as conn:
        if request.method == "POST":
            user_answer = request.form["answer"]
            new_question, next_id = next_question(conn)
            question_id = request.form["question_id"]
            answer = get_answer(conn, question_id)[0]
            result = answer == user_answer
            save_answer(conn, question_id, result)
            return render_template(
                "page.html",
                question=new_question,
                question_id=question_id,
                answer=answer,
                result=result,
            )
        else:
            question, question_id = next_question(conn)
            return render_template(
                "page.html", question=question, question_id=question_id
            )


def get_answer(conn, question_id):
    with conn.cursor() as cursor:
        cursor.execute(
            "select answer from questions where id = %(question_id)s",
            {"question_id": question_id},
        )
        answer = cursor.fetchone()
        return answer


def save_answer(conn, question_id, result):
    with conn.cursor() as cursor:
        cursor.execute(
            "insert into history (question_id, correct, ts) values (%(question_id)s, %(correct)s, current_timestamp)",
            {"question_id": question_id, "correct": result},
        )