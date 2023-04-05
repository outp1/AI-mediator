from typing import Union

from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.orm import Session

from bot.controllers import MenuController
from bot.models.users import User
from bot.utils import get_privacy_policy_keyboard
from config import config


async def start(message: Message, menu_controller: MenuController):
    user = await menu_controller.get_user_info(message.from_user.id)
    if config.privacy_policy and not user:
        return await message.answer(
            "Для пользования ботом, необходимо принять "
            f"<a href='{config.privacy_policy}'>политику конфидициальности</a>.",
            reply_markup=get_privacy_policy_keyboard(message.from_user.id),
        )
    else:
        if not user:
            await menu_controller.register_user(
                User(id=message.from_user.id, username=message.from_user.mention)
            )
        text, kb = await menu_controller.get_start_data()
        await message.answer(text, reply_markup=kb)


async def accept_privacy_policy(call: CallbackQuery, menu_controller: MenuController):
    user_id = int(call.data.split("_")[1])
    if user_id == call.from_user.id:
        await menu_controller.register_user(
            User(id=call.from_user.id, username=call.from_user.mention)
        )

        await call.message.delete()
        text, kb = await menu_controller.get_start_data()
        await call.message.answer(text, reply_markup=kb)
        await call.answer()
    else:
        return


def register_menu(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")

    dp.register_callback_query_handler(
        accept_privacy_policy,
        lambda call: call.data.startswith("privacypolicyaccept_"),
        state="*",
    )
