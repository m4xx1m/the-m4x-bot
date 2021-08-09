import os
import glob
import importlib.util
from aiogram import executor
from stickdistort.logger import log
from stickdistort.misc import dp


def init_modules():
    loaded_modules: list = []
    log.info(f"Loading modules")

    for _file in glob.glob(f"stickdistort/bot/modules/*.py"):
        _module_name = os.path.basename(_file).split(".py")[0]
        log.info(f"Loading module {_module_name}")

        _spec = importlib.util.spec_from_file_location(_module_name, _file)
        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
        _module.register()
        loaded_modules.append(_module_name)

    log.info(f"Loaded {len(loaded_modules)} modules: {', '.join(loaded_modules)}")


def start_pooling():
    executor.start_polling(dp, skip_updates=True)
