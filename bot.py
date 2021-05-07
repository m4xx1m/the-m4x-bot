import io
import json
import aiogram
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, executor

logging.basicConfig(
    format='[%(levelname)s][%(asctime)s] %(message)s',
    level=logging.INFO,
)

log = logging.getLogger(__name__)
log.level = logging.INFO
m4xx1m = 704477361
loop = asyncio.get_event_loop()
config = json.load(open("config.json"))

bot = Bot(token=config['bot_token'])
dp = Dispatcher(bot)

bot.parse_mode = "html"


def reg_handlers():
    @dp.message_handler(commands=['start'])
    async def starter(message: types.Message):
        await message.answer('да')


async def main():
    try:
        await bot.send_message(m4xx1m, "<b>Bot Started</b>")
    except Exception as err:
        log.error(f'Error sending start message: {err}')

        
if __name__ == '__main__':
    loop.run_until_complete(main())
    executor.start_polling(dp, skip_updates=True)