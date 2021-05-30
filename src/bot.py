import asyncio
import io
import json
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types, executor

from utils import DataBase, Distorting, AdminFilter, BotUtils
from utils.bot import format_all_commands

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
dp.filters_factory.bind(AdminFilter)
db = DataBase(config['dbName'], lang_cfgs=langs)
bot.parse_mode = "html"
bot.format_langs = langs
bot.bot_admins = db.get_admins()
bot_utils = BotUtils(user_langs=db.get_user_langs(), format_langs=langs, db=db)
compile_awl = bot_utils.compile_awl
check_user = bot_utils.check_user


def reg_handlers():
    @dp.message_handler(commands=['test'], is_admin=True)
    async def tester(message: types.Message):
        await message.reply((await bot.get_me())['username'])

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

        await message.reply(langs['start'])

    @dp.message_handler(commands=['help'])
    async def answer_help(message: types.Message):
        check_user(message.from_user)
        await message.reply(compile_awl(message.from_user.id, 'help',
                                        all_commands=format_all_commands(
                                            all_commands=langs['all_commands'],
                                            lang_code=db.get_lang(message.from_user.id)
                                        )))

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
            await message.reply('Only integer')

    @dp.message_handler(commands=['getadmins'], is_admin=True)
    async def getadmins(message: types.Message):
        await message.reply(
            text=compile_awl(
                uid=message.from_user.id,
                text='all_admins',
                bot_name=(await bot.get_me())['username'],
                admins='\n'.join([f'<a href="tg://user?id={uid}">{db.get_user(uid)["fname"]}</a>: {uid}' for uid in db.get_admins()])
            )
        )

    @dp.message_handler(commands=['deladmin'], is_admin=True)
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

    @dp.message_handler(commands=['setlang'])
    async def user_set_lang(message: types.Message):
        arg = message.get_args().split()[0]

        if arg not in langs['all_langs']:
            await message.reply(compile_awl(message.from_user.id, 'unknown_lang'))
            return

        if db.upd_user(uid=message.from_user.id, lang=arg):
            await message.reply(compile_awl(message.from_user.id, 'successfully'))
            return
        else:
            await message.reply(compile_awl(message.from_user.id, 'error_setting_lang'))
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

    @dp.message_handler(commands=['donate'])
    async def donate(message: types.Message):
        check_user(message.from_user)
        await message.reply(compile_awl(message.from_user.id, 'donate'), disable_web_page_preview=True)

    @dp.message_handler(commands=['contact'])
    async def contact(message: types.Message):
        check_user(message.from_user)
        await message.reply('\n'.join([f'<a href="tg://user?id={uid}">{name}</a>' for name, uid in config['authors'].items()]))

    @dp.message_handler(commands=['distort'])
    async def distort(message: types.Message):
        check_user(message.from_user)
        reply = message.reply_to_message

        if not reply:
            await message.reply(compile_awl(message.from_user.id, 'no_reply'))
            return
        if not reply.sticker or not reply.sticker.is_animated:
            await message.reply(compile_awl(message.from_user.id, 'not_animated'))
            return

        file = io.BytesIO()
        file.name = 'sticker.tgs'
        await bot.download_file_by_id(file_id=reply.sticker.file_id, destination=file)
        file.seek(0)

        distort_stickers = Distorting(
            input_file=file.read(),
            configs=config['distort_configs']
        )

        anim_configs = {}
        for num in range(1, len(config['distort_configs']) + 1):
            anim_configs[num] = 'Processing'

        anim_message = await message.reply(
            text=f'<b>Distorting!</b>\n' + '\n'.join(
                [f'<b>{str(num)}</b>: <code>{str(state)}</code>' for num, state in anim_configs.items()]
            )
        )

        async for num, file in distort_stickers:
            if file:
                ms = await bot.send_animation(chat_id=message.chat.id, animation=file,
                                              reply_to_message_id=reply.message_id)
                if not ms.sticker:
                    await ms.delete()
                    anim_configs[num] = 'Failed'
                    # await update_animation(anim_message, anim_configs)
                    continue
                anim_configs[num] = 'Done'
                # await update_animation(anim_message, anim_configs)
            else:
                anim_configs[num] = 'ERROR'
                # await update_animation(anim_message, anim_configs)

        await update_animation(anim_message, anim_configs)
        await asyncio.sleep(3)
        await anim_message.delete()
        db.plus_pdc(message.from_user.id)


async def update_animation(anim_message: types.Message, anim_cf):
    _txt = f'<b>Distorting!</b>\n' + '\n'.join(
        [f'<b>{str(num)}</b>: <code>{str(state)}</code>' for num, state in anim_cf.items()]
    )
    if anim_message.text != _txt:
        await anim_message.edit_text(_txt)


async def main():
    try:
        await bot.send_message(m4xx1m, "<b>Bot Started</b>")
    except Exception as err:
        log.error(f'Error sending start message: {err}')

    reg_handlers()


if __name__ == '__main__':
    db.run_updates(timeout=600)  # seconds # TODO: not forget to change timeout aahahah
    loop.run_until_complete(main())
    executor.start_polling(dp, skip_updates=True)
