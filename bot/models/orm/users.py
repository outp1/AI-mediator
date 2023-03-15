from sqlalchemy import JSON, Column, ForeignKey, String

from .base import BaseModel, BaseRepository


class UserModel(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True)


class ModeratorModel(BaseModel):
    __tablename__ = "moderators"

    user_id = Column(UserModel.id.type, ForeignKey(UserModel.id))
    appointed_by = Column(UserModel.id.type, default="root")
    permissions = Column(JSON, nullable=False, default={"all": True})
