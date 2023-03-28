import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery, Message

from bot.models import UsersRepository
from config import config


class UserFilter(BoundFilter):
    key = "is_user"

    def __init__(self, is_user: typing.Optional[bool] = None):
        self.is_user = is_user

    async def check(self, obj):
        if self.is_user is None:
            return False
        repo = UsersRepository(obj.bot.get("session"), obj.bot.get("db_repository"))
        result = bool(repo.get_by_id(obj.from_user.id)) == self.is_user
        if not result:
            if type(obj) == Message:
                await obj.reply(
                    "Зарегистрируйтесь в боте для выполнения данного"
                    "действия. Это можно сделать в личных сообщениях"
                    "со мной с помощью команды /start"
                )
        return result
