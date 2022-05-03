from flask import Flask, render_template, request
import psycopg2
from psycopg2 import pool
import os

# from algorithm import algo

POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
pool = pool.SimpleConnectionPool(1, 20, POSTGRESQL_URL)

app = Flask(__name__)


def next_question():
    with pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("select question, id from questions limit 1")
            question, question_id = cursor.fetchone()
            return question, question_id


@app.route("/", methods=["POST", "GET"])
def hello_world():
    if request.method == "POST":
        user_answer = request.form["answer"]
        new_question, next_id = next_question()
        question_id = request.form["question_id"]
        print("question_id", question_id)
        answer = get_answer(question_id)[0]
        result = answer == user_answer
        print("answer", answer)
        return render_template(
            "page.html", question=new_question, question_id=question_id, answer=answer,result=result
        )
    else:
        question, question_id = next_question()
        return render_template("page.html", question=question, question_id=question_id)


def get_answer(question_id):
    with pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "select answer from questions where id = %(question_id)s",
                {"question_id": question_id},
            )
            answer = cursor.fetchone()
            return answer
