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
        self.bot_config = bot_config if bot_config else None
        cur = self.con.cursor()

        def dict_factory(cursor,
                         row):  # https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.con.row_factory = dict_factory

        cur.execute(
            'CREATE TABLE IF NOT EXISTS users (date text, uid integer, fname text, username text, distort_count integer, \'limit\' integer)'
        )
        cur.execute(
            'CREATE TABLE IF NOT EXISTS admins (uid integer, fname text, username text)'
        )

        cur.execute(
            f'create table if not exists settings (uid integer, type text, {", ".join(self.bot_config["stock_settings"].keys())})'
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
        self.set_default_settings(uid)
        return True

    def get_settings(self, uid: int = None):
        cur = self.con.cursor()
        _sets = cur.execute('select * from settings where uid=?', (uid,)).fetchall()
        cur.close()
        if len(_sets) < 1:
            return None
        else:
            return _sets[0]

    def check_db(self, uids=None):
        cur = self.con.cursor()
        if not uids:
            uids = [uid['uid'] for uid in cur.execute('select uid from users')]

        # lang
        if self.lang_configs:
            for uid in uids:
                if self.get_lang(uid) not in self.lang_configs["all_langs"]:
                    self.upd_user(uid=uid, lang=self.lang_configs['default_lang'])
        else:
            log.error('Langs config doesn\'t exists')

        # limits
        log.info(
            f'{len([uid for uid in uids if self.get_limit(uid) != -1 and self.get_distort_count(uid) >= self.get_limit(uid)])} users exceeded the limit'
        )

    def upd_user(self, uid: int, date: str = None, fname: str = None, username: str = None, distort_count: int = None,
                 limit: int = None, lang: str = None, chat_type: str = None):
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
        if not chat_type:
            chat_type = userinfo['chat_type']

        cur.execute(
            'update users set '
            'date=:date, '
            'uid=:uid, '
            'fname=:fname, '
            'username=:username, '
            'distort_count=:distort_count, '
            '\'limit\'=:limit, '
            'lang=:lang, '
            'chat_type=:chat_type '
            'where uid=:uid',
            {'date': date, 'uid': uid, 'fname': fname, 'username': username, 'distort_count': distort_count,
             'limit': limit, 'lang': lang, 'chat_type': chat_type}
        )
        cur.close()
        return True

    def set_default_settings(self, uid):
        _upd_sets = {}
        for setting, param in self.bot_config['stock_settings'].items():
            _upd_sets.update({setting: param})
        return self.upd_user_settings(uid, **_upd_sets)

    def upd_user_settings(
            self,
            uid: int,
            chat_type: str = 'private',
            distort_without_command: bool = None,
            send_distort_status: bool = None,
            delete_distort_status: bool = None,
            delete_distort_status_timeout: int = None,
            use_chat_settings: bool = None,
            use_configs: str = None
    ):
        _user_sets = self.get_settings(uid)
        cur = self.con.cursor()

        if not distort_without_command and not isinstance(distort_without_command, bool):
            if _user_sets:
                distort_without_command = _user_sets['distort_without_command']
            else:
                distort_without_command = self.bot_config['stock_settings']['distort_without_command']
        if not send_distort_status and not isinstance(send_distort_status, bool):
            if _user_sets:
                send_distort_status = _user_sets['send_distort_status']
            else:
                send_distort_status = self.bot_config['stock_settings']['send_distort_status']
        if not delete_distort_status and not isinstance(delete_distort_status, bool):
            if _user_sets:
                delete_distort_status = _user_sets['delete_distort_status']
            else:
                delete_distort_status = self.bot_config['stock_settings']['delete_distort_status']
        if not delete_distort_status_timeout and not isinstance(delete_distort_status_timeout, bool):
            if _user_sets:
                delete_distort_status_timeout = _user_sets['delete_distort_status_timeout']
            else:
                delete_distort_status_timeout = self.bot_config['stock_settings']['delete_distort_status_timeout']
        if not use_chat_settings and not isinstance(use_chat_settings, bool):
            if _user_sets:
                use_chat_settings = _user_sets['use_chat_settings']
            else:
                use_chat_settings = self.bot_config['stock_settings']['use_chat_settings']
        if not use_configs:
            if _user_sets:
                use_configs = _user_sets['use_configs']
            else:
                use_configs = self.bot_config['stock_settings']['use_configs']

        if not _user_sets:
            cur.execute('insert into settings values('
                        ':uid, '
                        ':type, '
                        ':distort_without_command, '
                        ':send_distort_status, '
                        ':delete_distort_status, '
                        ':delete_distort_status_timeout, '
                        ':use_chat_settings, '
                        ':use_configs)',
                        {'uid': uid,
                         'type': chat_type,
                         'distort_without_command': distort_without_command,
                         'send_distort_status': send_distort_status,
                         'delete_distort_status': delete_distort_status,
                         'delete_distort_status_timeout': delete_distort_status_timeout,
                         'use_chat_settings': use_chat_settings,
                         'use_configs': use_configs
                         }
                        )
            self.con.commit()
            return True
        else:
            cur.execute('update settings set '
                        'distort_without_command=:distort_without_command, '
                        'send_distort_status=:send_distort_status, '
                        'delete_distort_status=:delete_distort_status, '
                        'delete_distort_status_timeout=:delete_distort_status_timeout, '
                        'use_chat_settings=:use_chat_settings, '
                        'use_configs=:use_configs '
                        'where uid=:uid',
                        {
                            'uid': uid,
                            'distort_without_command': distort_without_command,
                            'send_distort_status': send_distort_status,
                            'delete_distort_status': delete_distort_status,
                            'delete_distort_status_timeout': delete_distort_status_timeout,
                            'use_chat_settings': use_chat_settings,
                            'use_configs': use_configs
                        }
                        )
            return True

    def get_user_langs(self) -> dict:
        cur = self.con.cursor()
        _user_langs = {}
        for row in cur.execute('select uid, lang from users'):
            _user_langs[row['uid']] = row['lang']
        return _user_langs

    def get_user(self, uid: int):
        cur = self.con.cursor()
        user = cur.execute('select * from users where uid=:uid limit 1', {"uid": uid}).fetchall()
        if len(user) < 1:
            return None
        cur.close()
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

    def get_all_users(self):
        cur = self.con.cursor()
        return [uid['uid'] for uid in cur.execute('select uid from users').fetchall()]

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
        cur.close()
        return [admin['uid'] for admin in admins]

    def plus_dc(self, uid):
        return self.upd_user(uid, distort_count=self.get_user(uid)['distort_count'] + 1)

    def get_handle_stickers_chats(self):
        return [
            chat['uid']
            for chat in self.ex('select uid, distort_without_command from settings') if chat['distort_without_command']
        ]

    def ex(self, code, parameters=None):
        if parameters is None:
            parameters = {}
        cur = self.con.cursor()
        _out = cur.execute(code, parameters).fetchall()
        cur.close()
        return _out

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
