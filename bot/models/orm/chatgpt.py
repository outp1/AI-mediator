from sqlalchemy import Boolean, Column, ForeignKey, String

from .base import BaseID, BaseModel
from .users import UserModel


class ConversationModel(BaseModel):
    __tablename__ = "chatgpt_conversations"

    chat_id = Column(BaseID, nullable=False)
    created_by = Column(UserModel.id.type, ForeignKey(UserModel.id), nullable=False)
    is_stopped = Column(Boolean, nullable=False, default=False)


class ConversationRequestModel(BaseModel):
    __tablename__ = "chatgpt_conversation_requests"

    conversation_id = Column(
        ConversationModel.id.type,
        ForeignKey(ConversationModel.id),
        nullable=False,
    )
    user_id = Column(UserModel.id.type, ForeignKey(UserModel.id), nullable=False)
    prompt = Column(String, nullable=False)
    answer = Column(String)
