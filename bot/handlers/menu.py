from aiogram import Dispatcher
from aiogram.types import Message
from sqlalchemy.orm import Session

from bot.controllers import MenuController
from bot.models.users import User


async def start(message: Message, menu_controller: MenuController):
    user = User(id=message.from_user.id, username=message.from_user.mention)
    await menu_controller.register_user(user)
    text, reply_markup = await menu_controller.get_start_data()
    await message.answer(text, reply_markup=reply_markup)


def register_menu(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
