import io
import json
import os
import sys
from utils.db import DataBase
import aiogram
import asyncio
from datetime import datetime
import logging
from aiogram import Bot, Dispatcher, types, executor

logging.basicConfig(
    format='[%(levelname)s][%(asctime)s] %(message)s',
    level=logging.INFO,
)

db = DataBase('nn.db')
log = logging.getLogger(__name__)
log.level = logging.INFO
m4xx1m = 704477361
loop = asyncio.get_event_loop()
config = json.load(open("configs/botconfig.json"))
# langs = json.load(open("configs/langs.json"))

bot = Bot(token=config['bot_token'])
dp = Dispatcher(bot)

bot.parse_mode = "html"


def reg_handlers():
    @dp.message_handler(commands=['start'])
    async def starter(message: types.Message):
        if message.chat.type != "private":
            return

        db.new_user(
            date=str(datetime.utcnow()).split('.')[0],
            uid=message.from_user.id,
            fname=message.from_user.first_name,
            username=str(message.from_user.username),
        )

        log.info(f'New user! Name: {message.from_user.first_name}; ID: {message.from_user.id}; '
                                                                              f'Username: {message.from_user.username}')

        await message.reply('Hello there!')

    @dp.message_handler(commands=['getlang'])
    async def sendLang(message: types.Message):
        await message.reply(db.get_user_lang(message.from_user.id))

    @dp.message_handler(commands=['pdc'])
    async def pdc(message: types.Message):
        db.upd_DsC(message.from_user.id, db.get_DsC(message.from_user.id)+1)
async def main():
    try:
        await bot.send_message(m4xx1m, "<b>Bot Started</b>")
    except Exception as err:
        log.error(f'Error sending start message: {err}')

    reg_handlers()


if __name__ == '__main__':
    loop.run_until_complete(main())
    executor.start_polling(dp, skip_updates=True)
