from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from bot.models.orm.base import BaseID, Repository
from bot.models.orm.chatgpt import ConversationModel, ConversationRequestModel
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
    id: int
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
    created_at: datetime = datetime.now()
    is_stopped: bool = False
    thread_id: Optional[int] = None


class ConversationRequestsRepository(Repository):
    def __init__(self, session: Session, identity_map=None):
        self.session = session
        self.repository_name = "conversation_requests"
        self._identity_map = identity_map or {self.repository_name: {}}
        self.entity_class = ConversationRequest
        self.model_class = ConversationRequestModel

    def get_list_of_conversation_requests(self, conversation_id):
        result = []
        for request in self.list():
            if request.conversation_id == conversation_id:
                result.append(request)
        return result


class ConversationsRepository(Repository):
    def __init__(self, session: Session, identity_map=None):
        self.session = session
        self.repository_name = "conversations"
        self._identity_map = identity_map or {self.repository_name: {}}
        self.entity_class = Conversation
        self.model_class = ConversationModel

    def get_conversation_requests_history(self, conversation_id):
        requests_repo = ConversationRequestsRepository(self.session, self._identity_map)
        return ConversationRequestsHistory(
            conversation_id=conversation_id,
            requests=requests_repo.get_list_of_conversation_requests(conversation_id),
        )

    def get_by_chat_id(self, chat_id, is_stopped=False):
        result = (
            self.session.query(self.model_class)
            .filter_by(chat_id=chat_id, is_stopped=is_stopped)
            .one()
        )
        return self.model_to_entity(result)
