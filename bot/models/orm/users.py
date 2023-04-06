from sqlalchemy import JSON, Boolean, Column, ForeignKey, String

from .base import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True)
    privacy_policy = Column(Boolean, default=True)


class ModeratorModel(BaseModel):
    __tablename__ = "moderators"

    user_id = Column(UserModel.id.type, ForeignKey(UserModel.id))
    appointed_by = Column(UserModel.id.type, default="root")
    permissions = Column(JSON, nullable=False, default={"all": True})
