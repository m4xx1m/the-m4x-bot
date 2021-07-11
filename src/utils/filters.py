from aiogram.dispatcher.filters import BoundFilter
from aiogram import types


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        if not self.is_admin:
            return True
        return message.from_user.id in message.bot.bot_admins

