""" 
Algorithm for sending the right data to the frontend. 
State is stored in the db.
Query db, retrieve user data. Sort the user data according to the algorithm. 

examples:
history: {'question_id': 1, 'correct': True, 'ts': datetime.datetime(2022, 5, 4, 17, 54, 14, 675211)}
questions: {'id': 1, 'question': 'a?'}
"""
from collections import defaultdict
from typing import Tuple
from queue import PriorityQueue
import datetime

BASE_RATING = 400
K = 20


def rules(question_id):
    ...


def compute_elo(ratingA: int, ratingB: int, scoreA: bool) -> Tuple[int, int]:
    qA = 10 ** (ratingA / 400)
    qB = 10 ** (ratingB / 400)
    eA = qA / (qA + qB)
    eB = qB / (qA + qB)
    scoreB = 1 - scoreA
    ratingA = ratingA + K * (scoreA - eA)
    ratingB = ratingB + K * (scoreB - eB)
    return ratingA, ratingB


def time_to_forget(current_time, last_time, expected_time):
    time_diff = max((last_time - current_time).days, 1)
    return expected_time + time_diff


def time_history(history):
    """All questions start at 1 day. double or reset based on result"""
    time_score = defaultdict(lambda: 1)
    previous_time = {}
    for hist in history:
        question_id, correct, ts = hist.values()
        if correct:
            if question_id in previous_time:
                expected_time = time_score[question_id]
                time_score[question_id] = time_to_forget(
                    ts, previous_time[question_id], expected_time
                )
            else:
                time_score[question_id] = 2
        else:
            time_score[question_id] = 1
        previous_time[question_id] = ts
    return time_score


def return_scores(history):
    player_rating = BASE_RATING
    scores = defaultdict(lambda: BASE_RATING)
    for hist in history:
        question_id, correct, ts = hist.values()
        _, scores[question_id] = compute_elo(
            player_rating, scores[question_id], correct
        )
    return scores


def algo_learning(learning_qs, known_qs, history):
    time_history(history)
    scores = return_scores(history)
    pqueue = PriorityQueue()
    for k, v in scores.items():
        pqueue.put((v, k))
    return pqueue.get()


def algo_known():
    ...
