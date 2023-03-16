from dataclasses import dataclass
from re import L
from typing import List, Optional, Union

from sqlalchemy.orm import Session

from bot.models.orm.base import REMOVED, BaseID, BaseRepository, Repository
from bot.models.orm.chatgpt import ConversationModel, ConversationRequestModel
from bot.models.users import User
from config import config


@dataclass
class StartBotArgs:
    user_id: int
    chat_id: int
    thread_id: Optional[int] = None


@dataclass
class Chat:
    chat_id: int
    thread_id: Optional[int]
    authorized: bool
    admins: List[int]
    entering_user_id: Optional[int]
    timeout = config.chat_timeout


@dataclass
class ConversationRequest:
    conversation_id: int
    user_id: int
    prompt: str
    answer: str


@dataclass
class ConversationRequestsHistory:
    conversation_id: int
    requests: List[ConversationRequest]


@dataclass
class Conversation:
    id: BaseID
    chat_id: int
    created_by: int


class ConversationRepository(Repository):
    def __init__(self, session: Session, identity_map=None):
        self.session = session
        self.repository_name = "conversations"
        self._identity_map = identity_map or {self.repository_name: {}}
        self.entity_class = Conversation
        self.model_class = ConversationModel
