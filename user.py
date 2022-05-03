import flask_login


class User(flask_login.UserMixin):
    def __init__(self, email,password) -> None:
        super().__init__()
        self.email = email
        self.password = password

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
