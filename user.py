import flask_login
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash


class User(flask_login.UserMixin):
    @staticmethod
    def load_user(conn, user_id: int) -> Optional['User']:
        with conn.cursor() as cursor:
            cursor.execute("select email, password from users where id = %(user_id)s", {'user_id': user_id})
            row = cursor.fetchone()
            if row is None:
                return None
            return User(user_id, row[0], row[1])

    @staticmethod
    def new_user(conn, email, password) -> 'User':
        with conn.cursor() as cursor:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "insert into users (email, password) values (%(email)s, %(password)s) returning id",
                {'email': email, 'password': hashed_password}
            )
            user_id, = cursor.fetchone()
            return User(user_id, email, hashed_password)

    def __init__(self, user_id: int, email: str, hashed_password: str) -> None:
        self.user_id = user_id
        self.email = email
        self.hashed_password = hashed_password

    def get_id(self):
        return self.user_id

    @property
    def is_authenticated(self):
        return True
        # with pool.getconn() as conn:
        #     with conn.cursor() as cursor:
        #         cursor.execute(
        #             "select id from users where username = %(username)s",
        #             {"username": self.username},
        #         )
        #         answer = cursor.fetchone()
        #         return answer
