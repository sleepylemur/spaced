from typing import Optional, Tuple
from flask import render_template, request, Blueprint, g, redirect, url_for
from flask_login import login_required, current_user
from .globals import QuestionStatus
from .algorithm import algo_known, algo_learning


main = Blueprint("main", __name__)


@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


def next_question_sql():
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


def next_question_learning(learning, known, history) -> Tuple[str, int]:
    question, question_id = algo_learning(learning, known, history)
    return learning[0]["question"], learning[0]["id"]


def next_question_known(known, history) -> Tuple[str, int]:
    return known[0]["question"], known[0]["id"]


def next_question() -> Tuple[Optional[str], Optional[int]]:
    with g.conn.cursor() as cursor:
        cursor.execute(
            "select id, question, status from questions where status = any (%(statuses)s::question_status[]) and user_id = %(user_id)s",
            {
                "statuses": [QuestionStatus.LEARNING, QuestionStatus.KNOWN],
                "user_id": current_user.get_id(),
            },
        )
        question_rows = cursor.fetchall()
        questions = {QuestionStatus.LEARNING: [], QuestionStatus.KNOWN: []}
        for question_id, question, status in question_rows:
            questions[status].append({"id": question_id, "question": question})

        cursor.execute(
            "select correct, question_id, ts from history where user_id = %(user_id)s order by id desc",
            {"user_id": current_user.get_id()},
        )
        history = [
            {"question_id": row[1], "correct": row[0], "ts": row[2]}
            for row in cursor.fetchall()
        ]
    if len(questions[QuestionStatus.LEARNING]) > 0:
        return next_question_learning(
            questions[QuestionStatus.LEARNING], questions[QuestionStatus.KNOWN], history
        )
    if len(questions[QuestionStatus.KNOWN]) > 0:
        return next_question_known(questions[QuestionStatus.KNOWN], history)
    return None, None


@main.route("/add_questions", methods=["POST"])
@login_required
def add_questions():
    with g.conn.cursor() as cursor:
        cursor.execute(
            """update questions set status = 'learning' from
            (select id from questions where status = 'unknown' limit 5) as unknown_rows
            where questions.id = unknown_rows.id
            RETURNING questions.id;"""
        )
    g.conn.commit()
    # ids = [row[0] for row in cursor.fetchall()]
    return redirect(url_for("main.index"))


@main.route("/", methods=["POST", "GET"])
@login_required
def index():
    if request.method == "POST":
        user_answer = request.form["answer"]
        question_id = request.form["question_id"]
        answer = get_answer(question_id)
        result = answer == user_answer
        save_answer(int(question_id), result)
        return redirect(url_for("main.index", answer=answer, result=result))
    else:
        stats = get_stats()

        answer = request.args.get("answer")
        result = request.args.get("result")
        question, question_id = next_question()
        return render_template(
            "index.html",
            question=question,
            question_id=question_id,
            answer=answer,
            result=result,
            learning=stats[QuestionStatus.LEARNING],
            known=stats[QuestionStatus.KNOWN],
            unknown=stats[QuestionStatus.UNKNOWN],
        )


def get_stats():
    data = {
        QuestionStatus.KNOWN: 0,
        QuestionStatus.LEARNING: 0,
        QuestionStatus.UNKNOWN: 0,
    }
    with g.conn.cursor() as cursor:
        cursor.execute(
            "select count(*),status from questions where user_id = %(user_id)s group by status",
            {"user_id": current_user.get_id()},
        )
        res = cursor.fetchall()
        for k, v in res:
            data[v] = k
        return data


def get_answer(question_id):
    with g.conn.cursor() as cursor:
        cursor.execute(
            "select answer from questions where id = %(question_id)s and user_id = %(user_id)s",
            {"question_id": question_id, "user_id": current_user.get_id()},
        )
        (answer,) = cursor.fetchone()
        return answer


def save_answer(question_id: int, result: bool) -> None:
    required_count = 3
    with g.conn.cursor() as cursor:
        cursor.execute(
            "insert into history (question_id, correct, user_id) values (%(question_id)s, %(correct)s, %(user_id)s)",
            {
                "question_id": question_id,
                "correct": result,
                "user_id": current_user.get_id(),
            },
        )

        # if question status is learning and we got it right 3 times in a row, switch it to known
        cursor.execute(
            "select status from questions where id = %(question_id)s and user_id = %(user_id)s",
            {"question_id": question_id, "user_id": current_user.get_id()},
        )
        (status,) = cursor.fetchone()
        if status == QuestionStatus.LEARNING:
            cursor.execute(
                "select correct from history where question_id = %(question_id)s and user_id = %(user_id)s order by id desc limit %(required_count)s",
                {
                    "question_id": question_id,
                    "user_id": current_user.get_id(),
                    "required_count": required_count,
                },
            )
            correct_count = sum(correct for correct, in cursor.fetchall())
            if correct_count >= required_count:
                cursor.execute(
                    "update questions set status = %(status)s where id = %(question_id)s and user_id = %(user_id)s",
                    {
                        "question_id": question_id,
                        "user_id": current_user.get_id(),
                        "status": QuestionStatus.KNOWN,
                    },
                )
    g.conn.commit()
