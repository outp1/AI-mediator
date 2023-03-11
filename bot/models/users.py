from sqlalchemy import JSON, Column, ForeignKey, String

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True)


class Moderator(BaseModel):
    __tablename__ = "moderators"

    user_id = Column(User.id.type, ForeignKey(User.id))
    appointed_by = Column(User.id.type, default="root")
    permissions = Column(JSON, nullable=False, default={"all": True})
