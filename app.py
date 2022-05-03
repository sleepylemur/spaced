from flask import Flask, render_template
import psycopg2
import os

POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
pool = psycopg2.pool.SimpleConnectionPool(1, 20, POSTGRESQL_URL)

app = Flask(__name__)


@app.route("/")
def hello_world():
    with pool.get_conn() as conn:
        with conn.cursor() as cursor:
            query = cursor.execute("select * from questions")
            result = query.fetch_all()
            print(row for row in result)
    return render_template("page.html", question="yoyo")
