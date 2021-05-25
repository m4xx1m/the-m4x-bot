import logging
from datetime import datetime

import aiogram
from ..utils import DataBase

log = logging.getLogger('stickdistortbot_logger')
log.level = logging.INFO


class Bot(aiogram.Bot):
    @staticmethod
    async def answer(bot: aiogram.Bot, message: aiogram.types.Message, text: str, db: DataBase, langs: dict, **kwargs):
        uid = message.from_user.id
        userLang = db.get_lang(uid)

        if text not in langs.keys():
            log.error(f'{text} not found in lang strings')
            await message.reply('<b>ERROR</b>')
            return

        await message.answer(langs[text][userLang].format(**kwargs))


async def check_user(message: aiogram.types.Message, db: DataBase):
    if not db.get_user(message.from_user.id):
        db.new_user(
            date=str(datetime.utcnow()).split('.')[0],
            uid=message.from_user.id,
            fname=message.from_user.first_name,
            username=str(message.from_user.username),
        )