import json
import asyncio
from aiogram import Bot, Dispatcher, types
from bot.db import DataBase
from bot.logger import log

loop = asyncio.get_event_loop()

log.info("Initializing configs")
config = json.load(open("configs/botconfig.json", "r", encoding='utf-8'))
langs = json.load(open("configs/langs.json", "r", encoding='utf-8'))

log.info("Initializing database")
db = DataBase(lang_cfgs=langs, bot_config=config)
handle_stickers_chats = db.get_handle_stickers_chats()

log.info("Initializing aiogram bot")
bot = Bot(token=config['bot_token'])
dp = Dispatcher(bot)
loop.run_until_complete(
    bot.set_my_commands(
        commands=[
            types.BotCommand(command=_cmd, description=_descr) for _cmd, _descr in langs["all_commands"]["en"].items()
        ]
    )
)

from bot.utils import AdminFilter
dp.filters_factory.bind(AdminFilter)
bot.parse_mode = "html"
