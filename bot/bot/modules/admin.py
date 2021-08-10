import sys
import traceback
from meval import meval
from aiogram import types
from bot.logger import log
from bot.utils import compile_awl, get_uptime
from bot.misc import config, dp, db, bot


async def evalute_command(message: types.Message, is_exec=False):
    _answ_txt = []
    cmd = message.get_args()
    try:
        _allgl = globals()
        _allgl.update({'reply': message.reply_to_message})
        _allgl.update(locals())

        _executed = str(await meval(cmd, _allgl))

        if not _executed:
            _executed = 'None'

        while len(_executed) > 4096:  # message limit 4096 characters
            _answ_txt.append(_executed[:4096])
            _executed = _executed[4096:]
        _answ_txt.append(_executed)

        if len(_answ_txt) > config['max_msgs_in_eval']:
            _answ_txt[config['max_msgs_in_eval']] = 'Message too long'

        if not is_exec:
            for txt in _answ_txt[:config['max_msgs_in_eval'] + 1]:
                await message.reply(txt, parse_mode='')

    except Exception as err:
        try:
            exc = sys.exc_info()
            exc = "".join(traceback.format_exception(exc[0], exc[1], exc[2].tb_next.tb_next.tb_next))
        except:
            exc = err
        await message.reply(f'Failed expression:\n{exc}')


async def execute_command(message: types.Message):
    await evalute_command(message, is_exec=True)


async def add_admin(message: types.Message):
    uid = message.get_args().split()[0]

    if not db.get_user(int(uid)):
        _out = f'{uid} not found in db'
        log.error(_out)
        await message.reply(_out)
        return

    if uid.isdigit():
        await message.reply(db.add_admin(
            uid=int(uid),
            fname=db.get_fname(int(uid)),
            username=db.get_username(int(uid))
        ))
        # dp.filters_factory.unbind(AdminFilter)
        # dp.filters_factory.bind(AdminFilter)
        _out = f"{uid} was successfully added to the db"
        await message.reply(_out)
        log.info(_out)
        return
    else:
        await message.reply('Only integer')


async def get_statistics(message: types.Message):
    ms = await message.reply('<b>Loading...</b>')
    all_users = len(db.get_all_users())
    top_users = '\n'.join(
        [
            f'<a href="tg://user?id={user["uid"]}">{user["fname"]}</a>{(" [@" + user["username"] + "] ") if user["username"] != "None" else ""}: {user["distort_count"]}'
            for user in db.ex(
                'select distort_count, uid, fname, username from users order by distort_count desc limit :limit',
                {"limit": config['users_in_top']}
            )
        ]
    )
    total_usages = sum([dct["distort_count"] for dct in db.ex('select distort_count from users')])

    await ms.edit_text(
        f'''
<b>Users in bot: <code>{all_users}</code>
Total usages: <code>{total_usages}</code>
Bot uptime: <code>{get_uptime()}</code>

Top-{config["users_in_top"]} users:</b>\n{top_users}
'''
    )


async def get_admins(message: types.Message):
    await message.reply(
        text=compile_awl(
            uid=message.from_user.id,
            text='all_admins',
            bot_name=(await bot.get_me())['username'],
            admins='\n'.join(
                [f'<a href="tg://user?id={uid}">{db.get_user(uid)["fname"]}</a>: {uid}' for uid in db.get_admins()
                 if db.get_user(uid)])
        )
    )


async def del_admin(message: types.Message):
    arg = message.get_args().split()[0]

    if not arg.isdigit():
        await message.reply('Only integer')
        return

    await message.reply(str(db.del_admin(uid=int(arg))))
    # dp.filters_factory.unbind(AdminFilter)
    # dp.filters_factory.bind(AdminFilter)


async def set_limit(message: types.Message):
    args = message.get_args().replace('me', message.from_user.id).split()[0:1]
    for arg in args:
        if not arg.isdigit():
            await message.reply('Only integer')
            return

    await message.reply(db.upd_user(uid=int(args[0]), limit=int(args[1])))


def register():
    dp.register_message_handler(get_statistics, commands=['getstat'], is_admin=True)
    dp.register_message_handler(evalute_command, commands=['eval', 'e'], is_admin=True)
    dp.register_message_handler(add_admin, commands=['addadmin'], is_admin=True)
    dp.register_message_handler(del_admin, commands=['deladmin'], is_admin=True)
    dp.register_message_handler(set_limit, commands=['setlimit'], is_admin=True)
    dp.register_message_handler(execute_command, commands=['exec', 'ex'], is_admin=True)
    dp.register_message_handler(get_admins, commands=['getadmins'], is_admin=True)
