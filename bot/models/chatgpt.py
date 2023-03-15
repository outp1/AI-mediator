from dataclasses import dataclass
from typing import List, Optional

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
    chat_id: int
    created_by: int
    history: ConversationRequestsHistory
