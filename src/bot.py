import io
import json
import os
import sys
from utils import DataBase
import aiogram
import asyncio
from datetime import datetime
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types, executor

logging.basicConfig(
    format='[%(levelname)s][%(funcName)s][%(asctime)s] %(message)s',
    level=logging.INFO,
)

log = logging.getLogger('stickdistortbot_logger')
log.level = logging.INFO
m4xx1m = 704477361
loop = asyncio.get_event_loop()
config = json.load(open("configs/botconfig.json", encoding='utf-8'))
langs = json.load(open("configs/langs.json", encoding='utf-8'))

bot = Bot(token=config['bot_token'])
dp = Dispatcher(bot)
db = DataBase('nn.db')


bot.parse_mode = "html"


def reg_handlers():
    @dp.message_handler(commands=['getuser'])
    async def getuser(message: types.Message):
        await message.reply(str(db.get_user(message.from_user.id)))

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

        # log.info(f'New user! Name: {message.from_user.first_name}; ID: {message.from_user.id}; '
        #                                                                       f'Username: {message.from_user.username}')

        await message.reply('Hello there!')

    @dp.message_handler(commands=['getlang'])
    async def sendLang(message: types.Message):
        if message.chat.type != "private":
            return
        await message.reply(str(db.get_lang(message.from_user.id)))

    @dp.message_handler(commands=['pdc'], run_task=lambda ms: ms.from_user.id in db.get_admins())
    async def pdc(message: types.Message):
        if message.chat.type != "private":
            return
        db.upd_user(message.from_user.id, distort_count=db.get_user(message.from_user.id)['distort_count']+1)

    @dp.message_handler(commands=['getdsc'])
    async def getmydsc(message: types.Message):
        if message.chat.type != "private":
            return
        await message.reply(str(db.get_distort_count(message.from_user.id)))

    @dp.message_handler(commands=['getch'])
    async def getch(message: types.Message):
        await message.reply(db.con.total_changes)

    @dp.message_handler(commands=['stop_bd_updates'], run_task=lambda ms: ms.from_user.id in db.get_admins())
    async def stop_bd_updates(message: types.Message):
        await message.reply(str(db.stop_updates()))

    @dp.message_handler(commands=['run_bd_updates'], run_task=lambda ms: ms.from_user.id in db.get_admins())
    async def run_bd_updates(message: types.Message):
        await message.reply(str(db.run_updates(timeout=1)))

    @dp.message_handler(commands=['setlang'], run_task=lambda ms: ms.from_user.id in db.get_admins())
    async def user_set_lang(message: types.Message):
        args = message.get_args().split(' ')
        if len(args) != 2 or not args[0].isdigit() or not isinstance(args[1], str):
            log.error(f'Incorrect input values: {args}')
            return

        if args[1] not in langs['all_langs']:
            log.error(f'Lang {args[1]} does not exists')
            return

        await message.reply(str(
            db.upd_user(
                uid=int(args[0]),
                lang=args[1]
            )))

    @dp.message_handler(commands=['setuser'], run_task=lambda ms: ms.from_user.id in db.get_admins())
    async def setuser(message: types.Message):
        try:
            args = eval(message.get_args())
        except Exception as err:
            await message.reply(str(err))
            return

        if not isinstance(args, dict):
            return

        await message.reply(db.upd_user(**args))



async def main():
    try:
        await bot.send_message(m4xx1m, "<b>Bot Started</b>")
    except Exception as err:
        log.error(f'Error sending start message: {err}')

    reg_handlers()


if __name__ == '__main__':
    db.run_updates(timeout=5)
    loop.run_until_complete(main())
    executor.start_polling(dp, skip_updates=True)