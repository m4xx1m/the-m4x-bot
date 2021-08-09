import io
import asyncio
from aiogram import types
from datetime import datetime
from stickdistort import keyboards
from stickdistort.distorter import Distorting
from stickdistort.utils import check_user, compile_awl
from stickdistort.misc import db, dp, langs, config, bot
from stickdistort.logger import log


def format_all_commands(all_commands: dict, lang_code) -> str:
    return '\n'.join([f'/{key}: {value}' for key, value in all_commands[lang_code].items()])


async def update_animation(anim_message: types.Message, anim_cf):
    _txt = f'<b>Distorting!</b>\n' + '\n'.join(
        [f'<b>{str(num)}</b>: <code>{str(state)}</code>' for num, state in anim_cf.items()]
    )
    if anim_message.text != _txt:
        await anim_message.edit_text(_txt)


async def distort_without_command(message: types.Message):
    check_user(message.from_user)
    if message.chat.id:
        pass


async def setter(message: types.Message):
    await message.reply("Bot settings", reply_markup=keyboards.menu(compile_awl=compile_awl,
                                                                    **db.get_settings(message.from_user.id)))


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


async def answer_help(message: types.Message):
    check_user(message.from_user)
    await message.reply(compile_awl(message.from_user.id, 'help',
                                    all_commands=format_all_commands(
                                        all_commands=langs['all_commands'],
                                        lang_code=db.get_lang(message.from_user.id)
                                    )))


async def donate(message: types.Message):
    check_user(message.from_user)
    await message.reply(compile_awl(message.from_user.id, 'donate'), disable_web_page_preview=True)


async def contact(message: types.Message):
    check_user(message.from_user)
    await message.reply(
        '\n'.join([f'<a href="tg://user?id={uid}">{name}</a>' for name, uid in config['authors'].items()]))


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
                # await update_animation(anim_message, anim_configs) # floodwait :(
                continue
            anim_configs[num] = 'Done'
            # await update_animation(anim_message, anim_configs)
        else:
            anim_configs[num] = 'ERROR'
            # await update_animation(anim_message, anim_configs)

    await update_animation(anim_message, anim_configs)
    if len([state for state in anim_configs.values() if state == 'Failed' or state == 'ERROR']) == len(
            config['distort_configs']):
        return
    await asyncio.sleep(3)
    await anim_message.delete()
    db.plus_dc(message.from_user.id)


def register():
    dp.register_message_handler(setter, commands=['settings'])
    dp.register_message_handler(distort, commands=['distort'])
    dp.register_message_handler(answer_help, commands=['help'])
    dp.register_message_handler(donate, commands=['donate'], chat_type='private')
    dp.register_message_handler(starter, commands=['start'], chat_type='private')
    dp.register_message_handler(contact, commands=['contact'], chat_type='private')
    dp.register_message_handler(user_set_lang, commands=['setlang'], chat_type='private')
