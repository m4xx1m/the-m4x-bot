from aiogram import types
from .db import DataBase


class Langs:
    def __init__(
            self,
            db: DataBase,
            user_langs: dict = None,
            format_langs: dict =None
    ):
        self.db = DataBase
        self.user_langs = user_langs
        self.format_langs = format_langs
