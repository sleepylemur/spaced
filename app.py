from flask import Flask, render_template, request
import psycopg2
from psycopg2 import pool
import os


POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
pool = pool.SimpleConnectionPool(1, 20, POSTGRESQL_URL)

app = Flask(__name__)


def next_question(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            select question, id from questions limit 1
        """)
        question, question_id = cursor.fetchone()
        return question, question_id


@app.route("/", methods=["POST", "GET"])
def hello_world():
    with pool.getconn() as conn:
        if request.method == "POST":
            user_answer = request.form["answer"]
            new_question, next_id = next_question(conn)
            question_id = request.form["question_id"]
            answer = get_answer(conn, question_id)[0]
            result = answer == user_answer
            save_answer(conn, question_id, result)
            return render_template(
                "page.html", question=new_question, question_id=question_id, answer=answer,result=result
            )
        else:
            question, question_id = next_question(conn)
            return render_template("page.html", question=question, question_id=question_id)


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
            {'question_id': question_id, 'correct': result}
        )
