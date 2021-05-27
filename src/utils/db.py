import asyncio
import sqlite3
import logging

log = logging.getLogger('stickdistortbot_logger')
log.level = logging.INFO


class DataBase:
    def __init__(self, dbname: str, lang_cfgs: dict = None, bot_config: dict = None):
        self.con = sqlite3.connect(dbname)
        self.upd_task = None
        self.lang_configs = lang_cfgs
        self.stock_limit = bot_config['stock_limit'] if bot_config else -1
        cur = self.con.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS users (date text, uid integer, fname text, username text, distort_count integer, \'limit\' integer)'
        )
        cur.execute(
            'CREATE TABLE IF NOT EXISTS admins (uid integer, fname text, username text)'
        )
        cur.close()
        self.last_BD_ch = self.con.total_changes
        self.check_db()
        self.con.commit()

    def __enter__(self, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self.con.commit()
        self.con.close()

    def new_user(self, uid: int, date: str, fname: str, username: str, distort_count: int = 0, limit: int = None,
                 lang: str = 'en'):
        if self.get_user(uid):
            return False

        if not isinstance(limit, int):
            limit = self.stock_limit

        cur = self.con.cursor()
        cur.execute(
            "insert into users(date, uid, fname, username, distort_count, \'limit\', lang) "
            "values(:date, :uid, :fname, :username, :distort_count, :limit, :lang)",
            {"date": date, "uid": uid, "fname": fname, "username": username, "distort_count": distort_count,
             "limit": limit, "lang": lang}
        )
        cur.close()
        return True

    def check_db(self, uids=None):
        cur = self.con.cursor()
        if not uids:
            uids = [uid[0] for uid in cur.execute('select uid from users')]

        # lang
        if self.lang_configs:
            for uid in uids:
                if self.get_lang(uid) not in self.lang_configs["all_langs"]:
                    self.upd_user(uid=uid, lang=self.lang_configs['default_lang'])
        else:
            log.error('Langs config doesn\'t exists')

        # limits
        log.info(
            f'{len([uid for uid in uids if self.get_limit(uid) != -1 and self.get_distort_count(uid) >= self.get_limit(uid)])} users exceeded the limit')

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

        cur.execute(
            "update users set date=:date, uid=:uid, fname=:fname, username=:username, distort_count=:distort_count, 'limit'=:limit, lang=:lang where uid=:uid",
            {"date": date, "uid": uid, "fname": fname, "username": username, "distort_count": distort_count,
             "limit": limit, "lang": lang}
            )
        cur.close()
        return True

    def get_user_langs(self) -> dict:
        cur = self.con.cursor()
        _user_langs = {}
        for row in cur.execute('select uid, lang from users'):
            _user_langs[row[0]] = row[1]
        return _user_langs

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

    def add_admin(self, uid: int, fname: str, username: str):
        cur = self.con.cursor()
        cur.execute(
            'insert into admins(uid, fname, username) values(:uid, :fname, :username)',
            {"uid": uid, "fname": fname, "username": username}
        )
        cur.close()
        self.con.commit()
        return True

    def del_admin(self, uid: int):
        cur = self.con.cursor()
        cur.execute('delete from admins where uid=:uid', {"uid": uid})
        cur.close()
        self.con.commit()
        return True

    def get_admins(self):
        cur = self.con.cursor()
        admins = cur.execute('select uid from admins').fetchall()
        return [admin[0] for admin in admins]

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
