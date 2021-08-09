from datetime import datetime
from stickdistort.logger import log
from stickdistort.misc import db, langs


def compile_awl(  # Answer With Lang
        uid: int,
        text: str,
        **kwargs
):
    """Compiling text for answer"""
    user_langs = db.get_user_langs()

    if text not in langs.keys():
        log.error(f'{text} not found in lang strings')
        return

    ulang = user_langs.get(uid)
    if ulang not in langs[text].keys():
        ulang = 'en'

    return langs[text][ulang].format(
        **kwargs
    )


def check_user(user):
    if not db.get_user(user.id):
        db.new_user(
            date=str(datetime.utcnow()).split('.')[0],
            uid=user.id,
            fname=user.first_name,
            username=user.username,
        )
