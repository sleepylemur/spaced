from flask import (
    render_template,
    request,
    Blueprint,
    g
)
from flask_login import login_required
from .user import User


main = Blueprint("main", __name__)


@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


def next_question():
    with g.conn.cursor() as cursor:
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
@login_required
def index():
    if request.method == "POST":
        user_answer = request.form["answer"]
        question_id = request.form["question_id"]
        answer = get_answer(question_id)
        result = answer == user_answer
        save_answer(question_id, result)

        new_question, next_id = next_question()
        return render_template(
            "index.html",
            question=new_question,
            question_id=next_id,
            answer=answer,
            result=result,
        )
    else:
        question, question_id = next_question()
        return render_template(
            "index.html", question=question, question_id=question_id
        )


def get_answer(question_id):
    with g.conn.cursor() as cursor:
        cursor.execute(
            "select answer from questions where id = %(question_id)s",
            {"question_id": question_id},
        )
        return cursor.fetchone()[0]


def save_answer(question_id, result):
    with g.conn.cursor() as cursor:
        cursor.execute(
            "insert into history (question_id, correct, ts) values (%(question_id)s, %(correct)s, current_timestamp)",
            {"question_id": question_id, "correct": result},
        )
    g.conn.commit()
