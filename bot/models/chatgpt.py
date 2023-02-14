from typing import List, Optional

from pydantic import BaseModel

from config import config


class StartBotArgs(BaseModel):
    user_id: int
    chat_id: int
    thread_id: Optional[int]


class ChatModel(BaseModel):
    chat_id: int
    thread_id: Optional[int]
    authorized: bool
    admins: List[int]
    entering_user_id: Optional[int]
    timeout = config.chat_timeout
