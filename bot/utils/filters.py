from aiogram import types
from bot.misc import db
from aiogram.dispatcher.filters import BoundFilter


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        if not self.is_admin:
            return True
        return message.from_user.id in db.get_admins()
