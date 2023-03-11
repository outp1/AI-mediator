from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String

from config import config
from .base import BaseModel as BaseAlchemyModel
from .users import User


class StartBotArgs(BaseModel):
    user_id: int
    chat_id: int
    thread_id: Optional[int] = None


class ChatModel(BaseModel):
    chat_id: int
    thread_id: Optional[int]
    authorized: bool
    admins: List[int]
    entering_user_id: Optional[int]
    timeout = config.chat_timeout


class Conversation(BaseAlchemyModel):
    __tablename__ = "chatgpt_conversations"

    chat_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)


class ConversationRequest(BaseAlchemyModel):
    __tablename__ = "chatgpt_conversation_requests"

    chat_id = Column(
        Integer,
        ForeignKey(Conversation.id),
        nullable=False,
    )
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    prompt = Column(String, nullable=False)
    answer = Column(String)


# TODO orm relation
class ConversationRequests:
    pass
