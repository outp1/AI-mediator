import abc
import datetime
from dataclasses import fields
from typing import Union

from sqlalchemy import TIMESTAMP, BigInteger, Column, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()
metadata = MetaData()
BaseID = BigInteger
REMOVED = object()


class BaseModel(Base):
    __abstract__ = True

    id = Column(BaseID, nullable=False, unique=True, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f"<{type(self).__name__}(id={self.id})>"


class BaseRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, entity):
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, entity):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, id: BaseID) -> BaseModel:
        raise NotImplementedError

    def __getitem__(self, index) -> BaseModel:
        return self.get_by_id(index)


class Repository(BaseRepository):
    def __init__(
        self,
        session: Session,
        entity_class: type,
        model_class: type,
        repository_name=None,
        identity_map=None,
    ):
        self.session = session
        self._identity_map = identity_map or dict()
        self.entity_class = entity_class
        self.model_class = model_class
        self.repository_name = repository_name

    def model_to_entity(self, instance: BaseModel):
        class_fields = {f.name for f in fields(self.entity_class)}
        return self.entity_class(
            **{k: v for k, v in instance.__dict__.items() if k in class_fields}
        )

    def entity_to_model(self, entity):
        return self.model_class(**entity.__dict__)

    def _set_in_identity(self, index, value):
        if not self.repository_name:
            self._identity_map[index] = value
        else:
            self._identity_map[self.repository_name][index] = value

    def _get_in_identity(self, index=None):
        if not self.repository_name:
            if index:
                return self._identity_map.get(index, None)
            else:
                return self._identity_map
        else:
            if index:
                return self._identity_map[self.repository_name].get(index, None)
            else:
                return self._identity_map[self.repository_name]

    def add(self, entity):
        self._set_in_identity(entity.id, entity)
        instance = self.entity_to_model(entity)
        self.session.add(instance)

    def remove(self, entity):
        self._check_not_removed(entity)
        self._set_in_identity(entity.id, entity)
        model = self.session.query(self.model_class).get(entity.id)
        self.session.delete(model)

    def get_by_id(self, id):
        result = self._get_in_identity(id)
        if not result:
            result = self.session.query(self.model_class).get(id)
        if result:
            return self.model_to_entity(result)

    def list(self):
        list_ = self.session.query(self.model_class).all()
        result = []
        for entity in list_:
            result.append(self.model_to_entity(entity))
        return result

    def dict(self):
        _list = self.list()
        res = {}
        for item in _list:
            res[item.id] = item
        return res

    def _check_not_removed(self, entity):
        assert (
            self._get_in_identity(entity.id) is not REMOVED
        ), f"Entity {entity.id} already removed"

    def persist(self, entity):
        self._check_not_removed(entity)
        assert self._get_in_identity(entity.id), (
            "Cannon persist entity which is unknown to the repo. "
            "Did you forget to call repo.add() for this entity?"
        )
        instance = self.entity_to_model(entity)
        merged = self.session.merge(instance)
        self.session.add(merged)

    def persist_all(self):
        for id, user in self._get_in_identity().items():
            if user is not REMOVED:
                self.persist(user)
