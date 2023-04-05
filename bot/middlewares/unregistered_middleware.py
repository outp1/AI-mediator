from aiogram.dispatcher.handler import CancelHandler

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from bot.utils import get_privacy_policy_keyboard
from bot.filters.user_filter import UserFilter
from config import config


class UnregisteredMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_callback_query(self, call: CallbackQuery, data, *args):
        if await UserFilter(is_user=False).check(call):
            if call.data.split("_")[0] == "privacypolicyaccept":
                return
            if config.privacy_policy:
                text = (
                    "@{call.from_user.mention}, Чтобы пользоваться ботом "
                    "необходимо принять политику конфиденциальности - "
                    f"<a href='{config.privacy_policy}'>"
                    "Политика конфиденциальности</a>"
                )
                kb = get_privacy_policy_keyboard(call.from_user.id)
            else:
                text = (
                    f"@{call.from_user.mention}, зарегистрируйтесь в боте "
                    "для выполнения данного действия. Это можно сделать в личных "
                    "сообщениях со мной, с помощью команды /start"
                )
                kb = InlineKeyboardMarkup()
            await call.message.answer(text, reply_markup=kb)
            raise CancelHandler()

    async def on_process_message(self, message: Message, data, *args):
        if await UserFilter(is_user=False).check(message):
            command = data.get("command", None)
            if command:
                if command.command in config.unreg_ignore_commands:
                    return
            if config.privacy_policy:
                text = (
                    "Чтобы пользоваться ботом, необходимо принять "
                    "политику конфиденциальности - "
                    f"<a href='{config.privacy_policy}'>"
                    "Политика конфиденциальности</a>"
                )
                kb = get_privacy_policy_keyboard(message.from_user.id)
            else:
                text = (
                    "Зарегистрируйтесь в боте для выполнения данного "
                    "действия. Это можно сделать в личных сообщениях "
                    "со мной с помощью команды /start"
                )
                kb = InlineKeyboardMarkup()
            await message.reply(text, reply_markup=kb)
            raise CancelHandler()
