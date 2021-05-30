import json
import logging
from datetime import datetime
from .db import DataBase
from .lang_type import Langs
import aiogram
from aiogram import types

log = logging.getLogger('stickdistortbot_logger')
log.level = logging.INFO


def compile_awl(  # Answer With Lang
        message: types.Message,
        text: str,
        langs: Langs,
        all_commands: str = None,
        all_langs: list = None,
        **kwargs
):
    """Compiling text for answer"""
    uid = message.from_user.id

    if uid not in langs.user_langs.keys():
        with DataBase(dbname=json.load(open("configs/botconfig.json", encoding='utf-8'))['dbName']) as db:  # TODO: optimize it
            langs.user_langs = db.get_user_langs()

    if not langs.format_langs:
        langs.format_langs = json.load(open("configs/flangs.json", encoding='utf-8'))  # TODO: optimize it

    if text not in langs.format_langs.keys():
        log.error(f'{text} not found in lang strings')
        return

    ulang = langs.user_langs.get(uid)
    if ulang not in langs.format_langs[text].keys():
        ulang = 'en'

    return langs.format_langs[text][ulang].format(
        all_commands=all_commands,
        all_langs=all_langs,
        **kwargs
    )


def check_user(message: aiogram.types.Message, db: DataBase):
    if not db.get_user(message.from_user.id):
        db.new_user(
            date=str(datetime.utcnow()).split('.')[0],
            uid=message.from_user.id,
            fname=message.from_user.first_name,
            username=str(message.from_user.username),
        )


def format_all_commands(all_commands: dict, lang_code) -> str:
    return '\n'.join([f'/{key}: {value}' for key, value in all_commands[lang_code].items()])


def update_langs(db: DataBase):
    return db.get_user_langs()
