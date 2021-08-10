from bot.logger import log
from bot.misc import bot, loop


def register():
    try:
        loop.run_until_complete(bot.send_message(704477361, "<b>Bot Started</b>"))
    except Exception as err:
        log.error(f'Error sending start message: {err}')
