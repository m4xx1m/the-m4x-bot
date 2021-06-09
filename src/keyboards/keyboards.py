from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import *
import typing


def gen_kb(text_and_data):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    keyboard_markup.row(*row_btns)
    return keyboard_markup


def menu(
        uid: int,
        compile_awl,
        distort_without_command: bool,
        send_distort_status: bool,
        delete_distort_status: bool,
        delete_distort_status_timeout: int,
        *args,
        **kwargs
):
    rows = [
        (                                                                                   # row 1
            (
                f'{compile_awl(uid, "distort_without_command_settings")} | {"✅" if distort_without_command else "❌"}',  # button test
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


