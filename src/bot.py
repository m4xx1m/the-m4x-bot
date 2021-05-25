import io
import json
import os
import sys
from utils import DataBase, Distorter, AdminFilter
from utils.bot import answer, check_user
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
db = DataBase(config['dbName'], lang_cfgs=langs)
bot.parse_mode = "html"


def reg_handlers():
    dp.filters_factory.bind(AdminFilter)

    @dp.message_handler(commands=['start'], chat_type='private')
    async def starter(message: types.Message):
        if not db.get_user(message.from_user.id):
            db.new_user(
                date=str(datetime.utcnow()).split('.')[0],
                uid=message.from_user.id,
                fname=message.from_user.first_name,
                username=str(message.from_user.username)
            )

            log.info(f'New user! Name: {message.from_user.first_name}; ID: {message.from_user.id}; '
                     f'Username: {message.from_user.username}')

        await answer()

    @dp.message_handler(commands=['addadmin'], is_admin=True)
    async def addadmin(message: types.Message):
        uid = message.get_args().split()[0]

        if not db.get_user(int(uid)):
            await message.reply(f'{uid} not found in db')
            return

        if uid.isdigit():
            await message.reply(db.add_admin(
                uid=int(uid),
                fname=db.get_fname(int(uid)),
                username=db.get_username(int(uid))
            ))
            return
        else:
            log.error('Only integer')

    @dp.message_handler(commands=['getadmins'])
    async def getadmins(message: types.Message):
        await message.reply(str(db.get_admins()))

    @dp.message_handler(commands=['deladmin'])
    async def getadmins(message: types.Message):
        arg = message.get_args().split()[0]

        if not arg.isdigit():
            await message.reply('Only integer')
            return

        await message.reply(str(db.del_admin(uid=int(arg))))

    @dp.message_handler(commands=['stop_bd_updates'], is_admin=True)
    async def stop_bd_updates(message: types.Message):
        await message.reply(str(db.stop_updates()))

    @dp.message_handler(commands=['run_bd_updates'], is_admin=True)
    async def run_bd_updates(message: types.Message):
        await message.reply(str(db.run_updates()))

    @dp.message_handler(commands=['setlang'], is_admin=True)
    async def user_set_lang(message: types.Message):
        arg = message.get_args().split()[0]

        if arg[1] not in langs['all_langs']:
            # TODO: add answer
            return

        if db.upd_user(uid=message.from_user.id, lang=arg[1]):
            # TODO: add answer
            return
        else:
            # TODO: add answer
            return

    @dp.message_handler(commands=['p', 'ping'], is_admin=True)
    async def ping(message: types.Message):
        start = datetime.now()
        msg = await message.reply("[оk]")
        end = datetime.now()
        duration = (end - start).microseconds / 1000
        await msg.edit_text(f'[оk] {round(duration, 4)}ms')

    @dp.message_handler(commands=['setlimit'], is_admin=True)
    async def setlimit(message: types.Message):
        args = message.get_args().replace('me', message.from_user.id).split()[0:1]

        for arg in args:
            if not arg.isdigit():
                await message.reply('Only integer')
                return

        await message.reply(db.upd_user(uid=int(args[0]), limit=int(args[1])))

    @dp.message_handler(commands=['setuser'], is_admin=True)
    async def setuser(message: types.Message):
        try:
            args = eval(message.get_args())
        except Exception as err:
            await message.reply(str(err))
            return

        if not isinstance(args, dict):
            return

        await message.reply(db.upd_user(**args))

    @dp.message_handler(commands=['distort'])
    async def distort(message: types.Message):

        reply = message.reply_to_message

        if not reply:
            await message.reply('noreply')
            return
        if not reply.sticker:
            await message.reply('no stick')
            return
        if not reply.sticker.is_animated:
            await message.reply('not animated')
            return

        file = io.BytesIO()
        file.name = 'sticker.tgs'
        await bot.download_file_by_id(file_id=reply.sticker.file_id, destination=file)
        file.seek(0)

        ds = Distorter()
        distort_stickers = ds.distorting(
            input_file=file.read(),
            configs=config['distort_configs']
        )

        async for file in distort_stickers:
            ms = await bot.send_animation(chat_id=message.chat.id, animation=file,
                                          reply_to_message_id=message.message_id)
            if not ms.sticker:
                await ms.delete()
        # with open('tgs.tgs', 'wb') as f:
        #     f.write(file.read())


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
