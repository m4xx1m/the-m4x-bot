from aiogram import types
from stickdistort import keyboards
from stickdistort.misc import db, dp
from stickdistort.utils import compile_awl


async def inliner(query: types.CallbackQuery):
    answer_data = query.data
    _data = answer_data.split('|')
    command = _data[0]
    from_user = int(_data[1])
    if command in ['set']:
        param = _data[2]
        arg = eval(_data[3])
    else:
        param, arg = None, None

    if from_user != query.from_user.id:
        await query.answer('.__.')
        return

    if command == 'set':
        db.upd_user_settings(query.from_user.id, **{param: arg})
        # await query.answer('Done!')
        reply_markup = keyboards.menu(compile_awl=compile_awl, **db.get_settings(query.from_user.id))
        try:
            await query.message.edit_reply_markup(reply_markup=reply_markup)
        except:
            return
        return

    elif command == 'close':
        await query.message.delete()
        return


def register():
    dp.register_callback_query_handler(inliner)
