from aiogram import types
from datetime import datetime
from bot.logger import log
from bot.misc import db, dp


async def tester(message: types.Message):
    await message.answer('qq')


async def stop_bd_updates(message: types.Message):
    await message.reply(str(db.stop_updates()))


async def run_bd_updates(message: types.Message):
    await message.reply(str(db.run_updates()))


async def ping(message: types.Message):
    start = datetime.now()
    msg = await message.reply("[оk]")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await msg.edit_text(f'[оk] {round(duration, 4)}ms')


async def db_pusher(message: types.Message):
    db.con.commit()
    log.info('Force DB update')
    await message.reply("Pushed")


def register():
    dp.register_message_handler(tester, commands=['test'])
    dp.register_message_handler(ping, commands=['p', 'ping'], is_admin=True)
    dp.register_message_handler(db_pusher, commands=['push_db'], is_admin=True)
    dp.register_message_handler(run_bd_updates, commands=['run_bd_updates'], is_admin=True)
    dp.register_message_handler(stop_bd_updates, commands=['stop_bd_updates'], is_admin=True)
