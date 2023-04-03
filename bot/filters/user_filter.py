from typing import Optional

from aiogram.dispatcher.filters import BoundFilter

from bot.models import UsersRepository


class UserFilter(BoundFilter):
    key = "is_user"

    def __init__(self, is_user: Optional[bool] = None):
        self.is_user = is_user

    async def check(self, obj):
        if self.is_user is None:
            return False
        repo = UsersRepository(obj.bot.get("session"), obj.bot.get("db_repository"))
        return bool(repo.get_by_id(obj.from_user.id)) == self.is_user
