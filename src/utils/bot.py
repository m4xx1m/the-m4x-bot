import json
import logging
from datetime import datetime
from .db import DataBase
import aiogram
from aiogram import types

log = logging.getLogger('stickdistortbot_logger')
log.level = logging.INFO


class AnswerCompiler:
    def __init__(self, user_langs, format_langs):
        self.user_langs = user_langs
        self.format_langs = format_langs

    def compile_awl(  # Answer With Lang
            self,
            uid: int,
            text: str,
            all_commands: str = None,
            all_langs: list = None,
            **kwargs
    ):
        """Compiling text for answer"""
        if uid not in self.user_langs.keys():
            with DataBase(dbname=json.load(open("configs/botconfig.json", encoding='utf-8'))['dbName']) as db:
                self.user_langs = db.get_user_langs()

        if not self.format_langs:
            self.format_langs = json.load(open("configs/langs.json", encoding='utf-8'))

        if text not in self.format_langs.keys():
            log.error(f'{text} not found in lang strings')
            return

        ulang = self.user_langs.get(uid)
        if ulang not in self.format_langs[text].keys():
            ulang = 'en'

        return self.format_langs[text][ulang].format(
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
