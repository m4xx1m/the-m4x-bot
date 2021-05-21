import sqlite3


class DataBase:
    def __init__(self, dbname: str):
        self.con = sqlite3.connect(dbname)
        cur = self.con.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS users (date text, uid integer, fname text, username text, distort_count integer, \'limit\' integer)'
        )

    def new_user(self, date: str, uid: int, fname: str, username: str, distort_count: int = 0, limit: int = -1, lang: str = "en"):
        cur = self.con.cursor()
        cur.execute(
            "INSERT INTO users(date, uid, fname, username, distort_count, \'limit\', lang)"
            " SELECT * FROM (SELECT :date, :uid, :fname, :username, :distort_count, :limit, :lang) AS tmp"
            " WHERE NOT EXISTS (SELECT uid FROM users WHERE uid=:uid) LIMIT 1",
            {"date": date, "uid": uid, "fname": fname, "username": username, "distort_count": distort_count, "limit": limit, "lang": lang}
        )
        cur.close()
        self.con.commit()

    def upd_user(self, uid: int, **kwargs):
        pass

    def get_DsC(self, uid: int):
        cur = self.con.cursor()
        return cur.execute("SELECT distort_count FROM users WHERE uid=?", (uid,)).fetchall()[0][0]

    def upd_DsC(self, uid: int, distort_count: int):
        cur = self.con.cursor()
        cur.execute("UPDATE users SET distort_count = ? where uid = ?", (distort_count, uid))
        self.con.commit()

    def plus_DsC(self, uid: int):
        self.upd_DsC(
            uid,
            self.get_DsC(uid) + 1
        )

    def updDB(self, users: list):
        for uid, fname, username, distort_count, limit, lang in users:
            cur = self.con.cursor()
            cur.execute(
                "update users(uid, distort_count, limit, lang)"
                " set distort_count = :distort_count, limit = :limit, lang = :lang where uid = ?",
                {"uid": uid, "fname": fname, "username": username, "distort_count": distort_count, "limit": limit, "lang": lang}
            )

    def get_limit(self, uid: int):
        cur = self.con.cursor()
        return cur.execute("SELECT limit FROM users WHERE uid=?", (uid,)).fetchall()[0][0]

    def upd_limit(self, uid: int, limit: int):
        cur = self.con.cursor()
        cur.execute("UPDATE users SET limit = ? where uid = ?", (limit, uid))
        self.con.commit()

    def get_user_lang(self, uid: int):
        cur = self.con.cursor()
        return cur.execute("SELECT lang FROM users WHERE uid=?", (uid,)).fetchall()[0][0]

    def upd_user_lang(self, uid: int, lang: str):
        cur = self.con.cursor()
        cur.execute("UPDATE users SET lang = ? where uid = ?", (lang, uid))
        self.con.commit()
