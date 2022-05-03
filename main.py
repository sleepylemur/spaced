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
            with next_questions as (
                select id, question_id, lead(question_id) over (order by id) from history
            ),
            blocked as (
                (
                    -- block questions from happening in the same order as they were seen last time
                    select lead as blocked_id from next_questions
                    where
                        question_id = (select question_id from history order by id desc limit 1)
                        and lead is not null
                    order by id desc
                    limit 1
                ) union (
                    -- block the same question from being shown twice in a row
                    select question_id as blocked_id
                    from history
                    order by id desc
                    limit 1
                )
            ),
            question_age as (
                select question_id, min(row_number) as age from (
                    select question_id, row_number() over (order by id desc)
                    from history
                ) as inner_query
                where question_id != all (select blocked_id from blocked)
                group by question_id
            ),
            unseen_questions as (
                select questions.id
                from questions
                left join history on questions.id = history.question_id
                where history.question_id is null
            )
            select question, id from questions where id =
                case when exists(select 1 from unseen_questions) then
                    (select id from unseen_questions limit 1)
                else
                    (select question_id from question_age order by age desc limit 1)
                end;
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


# @app.route("/", methods=["POST", "GET"])
# def hello_world():
#     conn = pool.getconn()
#     try:
#         if request.method == "POST":
#             user_answer = request.form["answer"]
#             question_id = request.form["question_id"]
#             answer = get_answer(conn, question_id)[0]
#             result = answer == user_answer
#             save_answer(conn, question_id, result)

#             new_question, next_id = next_question(conn)
#             return render_template(
#                 "page.html",
#                 question=new_question,
#                 question_id=next_id,
#                 answer=answer,
#                 result=result,
#             )
#         else:
#             question, question_id = next_question(conn)
#             return render_template("page.html", question=question, question_id=question_id)
#     finally:
#         pool.putconn(conn)




def save_answer(conn, question_id, result):
    with conn.cursor() as cursor:
        cursor.execute(
            "insert into history (question_id, correct, ts) values (%(question_id)s, %(correct)s, current_timestamp)",
            {"question_id": question_id, "correct": result},
        )
