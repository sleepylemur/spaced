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
        question_id = request.args["question_id"]
        return get_answer(question_id)
    else:
        question, question_id = next_question()
        return render_template("page.html", question=question, question_id=question_id)


def get_answer(question_id):
    with pool.getconn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("select question, id from questions limit 1")
            question, question_id = cursor.fetchone()
            return question, question_id
