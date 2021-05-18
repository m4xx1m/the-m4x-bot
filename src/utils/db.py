import sqlite3


class DataBase:
    def __init__(self):
        self.con = sqlite3.connect('../nn.db')
        self.cur = self.con.cursor()
        self.cur.execute(
            'CREATE TABLE IF NOT EXISTS users (date text, uid integer, fname text, username text, distort_count integer, \'limit\' integer)'
        )
        self.cur.execute('ALTER TABLE users ADD COLUMN lang text')

    def new_user(self, date: str, uid: int, fname: str, username: str, distort_count: int = 0, limit: int = -1):
        self.cur.execute(
            "INSERT INTO users(date, uid, fname, username, distort_count, \'limit\') SELECT * FROM (SELECT ?, ?, ?, ?, ?, ?) AS tmp WHERE NOT EXISTS (SELECT uid FROM users WHERE uid=?) LIMIT 1",
            (date, uid, fname, username, distort_count, limit, uid)
        )
        self.con.commit()

    def upd_DsC(self, uid: int, distort_count: int):
        self.cur.execute("UPDATE users SET distort_count = ? where id = ?", (distort_count, uid))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
