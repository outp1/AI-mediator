from dataclasses import dataclass
from typing import Optional, Union, List
from sqlalchemy import Integer

from sqlalchemy.orm import Session

from .orm.base import BaseRepository, REMOVED
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


class UsersRepository(BaseRepository):
    def __init__(self, session: Session, identity_map=None):
        self.session = session
        self._identity_map = identity_map or {"users": {}}

    def user_model_to_entity(self, instance: UserModel):
        return User(id=instance.id, username=instance.username)

    def user_entity_to_model(self, user: User):
        return UserModel(id=user.id, username=user.username)

    def add(self, user: Union[User, UserModel]):
        self._identity_map["users"][user.id] = user
        instance = self.user_entity_to_model(user)
        self.session.add(instance)

    def remove(self, user: User):
        self._check_not_removed(user)
        self._identity_map["users"][user.id] = REMOVED
        listing_model = self.session.query(UserModel).get(user.id)
        self.session.delete(listing_model)

    def get_by_id(self, id) -> Optional[User]:
        result = self._identity_map["users"].get(id, None)
        if not result:
            result = self.session.query(UserModel).get(id)
        if result:
            return self.user_model_to_entity(result)

    def list(self) -> List[User]:
        list_ = self.session.query(UserModel).all()
        result = []
        for user in list_:
            result.append(self.user_model_to_entity(user))
        return result

    def dict(self):
        _list = self.list()
        res = {}
        for item in _list:
            res[item.id] = item
        return res

    def _check_not_removed(self, entity):
        assert (
            self._identity_map["users"].get(entity.id, None) is not REMOVED
        ), f"Entity {entity.id} already removed"

    def persist(self, user: User):
        self._check_not_removed(user)
        assert user.id in self._identity_map["users"], (
            "Cannon persist entity which is unknown to the repo. "
            "Did you forget to call repo.add() for this entity?"
        )
        instance = self.user_entity_to_model(user)
        merged = self.session.merge(instance)
        self.session.add(merged)

    def persist_all(self):
        for id, user in self._identity_map["users"].items():
            if user is not REMOVED:
                self.persist(user)
