from aiogram import types


def menu(
        uid: int,
        compile_awl,
        distort_without_command: bool,
        send_distort_status: bool,
        delete_distort_status: bool,
        delete_distort_status_timeout: int,
        **kwargs
):
    rows = [
        (                                                                                   # row 1
            (
                f'{compile_awl(uid, "distort_without_command_settings")} | {"✅" if distort_without_command else "❌"}',  # button text
                f'set|{uid}|distort_without_command|{not distort_without_command}'          # button data
            ),
        ),

        (                                                                                   # row 2
            (
                f'{compile_awl(uid, "send_distort_status_settings")} | {"✅" if send_distort_status else "❌"}',
                f'set|{uid}|send_distort_status|{not send_distort_status}'
            ),

        ),

        (
            (
                f'{compile_awl(uid, "delete_distort_status_settings")} | {"✅" if delete_distort_status else "❌"}',
                f'set|{uid}|delete_distort_status|{not delete_distort_status}'
            ),
        ),

        (
            (
                f'{compile_awl(uid, "delete_distort_status_timeout_settings")} | {delete_distort_status_timeout}',
                f'set|{uid}|delete_distort_status_timeout|None'
            ),
        ),
        (
            (
                '+',
                f'set|{uid}|delete_distort_status_timeout|{delete_distort_status_timeout+1}'
            ),
            (
                '-',
                f'set|{uid}|delete_distort_status_timeout|{delete_distort_status_timeout - 1}'
            )
        ),

        (
            (
                f'{compile_awl(uid, "close_settings")}',
                f'close|{uid}'
            ),
        ),
    ]

    keyboard_markup = types.InlineKeyboardMarkup()

    for row in rows:
        row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in row)
        keyboard_markup.row(*row_btns)

    return keyboard_markup
