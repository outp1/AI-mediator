from dataclasses import dataclass

from sqlalchemy.orm import Session

from .orm.base import Repository
from .orm.users import UserModel

UserID = int


@dataclass
class User:
    id: UserID
    username: str
    privacy_policy: bool = True


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
