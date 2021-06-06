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
                f'Distort without command | {"ON" if distort_without_command else "OFF"}',  # button test
                f'set|{uid}|distort_without_command|{not distort_without_command}'          # button data
            ),
        ),

        (                                                                                   # row 2
            (
                f'Send distort status | {"ON" if send_distort_status else "OFF"}',
                f'set|{uid}|send_distort_status|{not send_distort_status}'
            ),

        ),

        (
            (
                f'Delete distort status | {"ON" if delete_distort_status else "OFF"}',
                f'set|{uid}|delete_distort_status|{not delete_distort_status}'
            ),
        ),

        (
            (
                f'Delete distort status timeout | {delete_distort_status_timeout}',
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
                'Close',
                f'close|{uid}|None|None'
            ),
        ),
    ]

    keyboard_markup = types.InlineKeyboardMarkup()

    for row in rows:
        row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in row)
        keyboard_markup.row(*row_btns)

    return keyboard_markup


