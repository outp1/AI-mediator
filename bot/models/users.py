from dataclasses import dataclass
from typing import Union

from sqlalchemy import Integer
from sqlalchemy.orm import Session

from .orm.base import REMOVED, BaseRepository, Repository
from .orm.users import UserModel

UserID = Integer


@dataclass
class User:
    id: UserID
    username: str


@dataclass
class Moderator:
    user_id: UserID
    appointed_by: str
    permissions: str


class UsersRepository(Repository):
    def __init__(self, session: Session, identity_map=None):
        self.session = session
        self.repository_name = "users"
        self._identity_map = identity_map or {self.repository_name: {}}
        self.entity_class = User
        self.model_class = UserModel
