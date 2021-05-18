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

db = DataBase()
log = logging.getLogger(__name__)
log.level = logging.INFO
m4xx1m = 704477361
loop = asyncio.get_event_loop()
config = json.load("configs/botconfig.json")
langs = json.load("configs/langs.json")

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

async def main():
    try:
        await bot.send_message(m4xx1m, "<b>Bot Started</b>")
    except Exception as err:
        log.error(f'Error sending start message: {err}')

    reg_handlers()


if __name__ == '__main__':
    loop.run_until_complete(main())
    executor.start_polling(dp, skip_updates=True)
