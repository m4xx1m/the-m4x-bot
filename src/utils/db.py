import asyncio
import sqlite3
import logging

log = logging.getLogger('stickdistortbot_logger')
log.level = logging.INFO


class DataBase:
    def __init__(self, dbname: str):
        self.con = sqlite3.connect(dbname)
        self.upd_task = None
        cur = self.con.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS users (date text, uid integer, fname text, username text, distort_count integer, \'limit\' integer)'
        )
        cur.execute(
            'CREATE TABLE IF NOT EXISTS admins (uid integer, fname text, username text)'
        )
        cur.close()
        self.last_BD_ch = self.con.total_changes
        self.con.commit()

    def new_user(self, uid: int, date: str, fname: str, username: str, distort_count: int = 0, limit: int = -1,
                 lang: str = 'en'):
        if self.get_user(uid):
            return False
        cur = self.con.cursor()
        cur.execute(
            "insert into users(date, uid, fname, username, distort_count, \'limit\', lang) "
            "values(:date, :uid, :fname, :username, :distort_count, :limit, :lang)",
            {"date": date, "uid": uid, "fname": fname, "username": username, "distort_count": distort_count,
             "limit": limit, "lang": lang}
        )
        cur.close()
        return True

    def upd_user(self, uid: int, date: str = None, fname: str = None, username: str = None, distort_count: int = None,
                 limit: int = None, lang: str = None):
        userinfo = self.get_user(uid)
        if not userinfo:
            return False
        cur = self.con.cursor()

        if not date:
            date = userinfo['date']
        if not fname:
            fname = userinfo['fname']
        if not username:
            username = userinfo['username']
        if not distort_count:
            distort_count = userinfo['distort_count']
        if not limit:
            limit = userinfo['limit']
        if not lang:
            lang = userinfo['lang']

        cur.execute("update users set date=:date, uid=:uid, fname=:fname, username=:username, distort_count=:distort_count, 'limit'=:limit, lang=:lang where uid=:uid",
                    {"date": date, "uid": uid, "fname": fname, "username": username, "distort_count": distort_count,
                     "limit": limit, "lang": lang}
                    )
        cur.close()
        return True

    @staticmethod
    def to_dict(user: tuple) -> dict:
        return {
            "date": user[0],
            "uid": user[1],
            "fname": user[2],
            "username": user[3],
            "distort_count": user[4],
            "limit": user[5],
            "lang": user[6]
        }

    def get_user(self, uid: int, to_dict=True):
        cur = self.con.cursor()
        user = cur.execute('select * from users where uid=:uid limit 1', {"uid": uid}).fetchall()
        if len(user) < 1:
            return None
        cur.close()
        if to_dict:
            return self.to_dict(user[0])
        else:
            return user[0]

    def get_date(self, uid):
        return self.get_user(uid)['date']

    def get_fname(self, uid):
        return self.get_user(uid)['fname']

    def get_username(self, uid):
        return self.get_user(uid)['username']

    def get_distort_count(self, uid):
        return self.get_user(uid)['distort_count']

    def get_limit(self, uid):
        return self.get_user(uid)['limit']

    def get_lang(self, uid):
        return self.get_user(uid)['lang']

    def get_admins(self):
        pass

    def run_updates(self, timeout: int = 5):
        if not self.upd_task or self.upd_task.cancelled():
            self.upd_task = asyncio.get_event_loop().create_task(self._run_updates(timeout))
            return True
        else:
            return False

    def stop_updates(self):
        if self.upd_task or not self.upd_task.cancelled():
            self.upd_task.cancel()
            return True
        else:
            return False

    async def _run_updates(self, timeout: int):
        while True:
            await asyncio.sleep(timeout)
            if self.last_BD_ch != self.con.total_changes:
                self.con.commit()
                log.info('Updating DB')
                self.last_BD_ch = self.con.total_changes
