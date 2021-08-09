import logging

file_log = logging.FileHandler(filename='log.txt', mode="a", encoding="utf-8")
console_out = logging.StreamHandler()
logging.basicConfig(
    format='[%(levelname)s][%(funcName)s][%(asctime)s] %(message)s',
    level=logging.INFO,
    handlers=(file_log, console_out)
)
logging.getLogger("aiogram").setLevel(logging.WARNING)
log = logging.getLogger('stickdistortbot_logger')
