import abc
import datetime
import uuid

from sqlalchemy import TIMESTAMP, Column, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = MetaData()
BaseID = Integer
REMOVED = object()


class BaseModel(Base):
    __abstract__ = True

    id = Column(BaseID, nullable=False, unique=True, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return f"<{type(self).__name__}(id={self.id})>"


class BaseRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, entity: BaseModel):
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, entity: BaseModel):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id(self, id: BaseID) -> BaseModel:
        raise NotImplementedError

    def __getitem__(self, index) -> BaseModel:
        return self.get_by_id(index)
