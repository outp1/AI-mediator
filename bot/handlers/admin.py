from aiogram import Dispatcher
from aiogram.types import Message


async def admin_test(message: Message):
    await message.answer(text="Вы администратор.")


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_test, commands=["admin"], is_admin=True, state="*"
    )
