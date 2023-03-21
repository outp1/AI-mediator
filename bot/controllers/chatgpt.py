from datetime import datetime
import logging
from typing import Dict, List, Optional

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.orm import Session

from bot.models.chatgpt import (
    Chat,
    Conversation,
    ConversationRequest,
    ConversationRequestsRepository,
    ConversationsRepository,
    StartBotArgs,
)
from bot.repos.chatgpt import OpenAIRepo
from config import config
from utils.id_generator import generate_base_id


class ChatGPTController:
    def __init__(self, db_session: Session, db_repository: dict):
        self.chats: Dict[int, Chat] = {}
        self.repo = OpenAIRepo()
        self.logger = logging.getLogger("telegram_bot.ChatGPTController")
        self.db_session = db_session
        self.conversations_repo = ConversationsRepository(db_session, db_repository)
        self.conv_requests_repo = ConversationRequestsRepository(
            db_session, db_repository
        )
        for chat in self.conversations_repo.list():
            self.chats[chat["chat_id"]] = chat

    async def start(self, args: StartBotArgs):
        if args.chat_id in self.chats.keys() and self.chats[args.chat_id].authorized:
            return "Password actually accepted"
        chat = Chat(
            chat_id=args.chat_id,
            thread_id=args.thread_id,
            authorized=False,
            admins=[],
            entering_user_id=args.user_id,
        )
        self.chats[args.chat_id] = chat
        self.logger.debug("Started chat authorization")
        return "Please enter the password"

    def login_filters(self, message: Message):
        return (
            message.chat.id in self.chats.keys()
            and message.from_user.id == self.chats[message.chat.id].entering_user_id
        )

    async def login(self, chat_id, password, user_id):
        chat = self.chats[chat_id]
        result = "Invalid password, access denied."
        if password in config.chatgpt_passwords and user_id == chat.entering_user_id:
            chat.authorized = True
            chat.admins.append(user_id)
            chat.entering_user_id = None
            result = "Password accepted, how can I help you today?"
            self.conversations_repo.add(
                Conversation(
                    generate_base_id(self.conversations_repo.get_by_id),
                    chat_id,
                    user_id,
                    datetime.now(),
                )
            )
            self.db_session.commit()
            self.logger.debug("Authorized new chat")
        else:
            chat.entering_user_id = None
            self.logger.debug(
                f"Authorization failed. Wrong password entered: {password}"
            )

        self.chats[chat_id] = chat
        return result

    def process_message_filters(self, message: Message):
        chat_id = message.chat.id
        thread_id = message.message_thread_id
        request = message.text
        return (
            chat_id in self.chats.keys()
            and self.chats[chat_id].authorized
            and self.chats[chat_id].thread_id == thread_id
            and not request.startswith("!")
            and not request.startswith("/")
        )

    async def process(self, request: str, chat_id, user_id, disable_proxy=False):
        self.logger.debug(f"Sending request with prompt:\n{request}")
        answer = await self.repo.send_request(request, disable_proxy=disable_proxy)
        conversation_id = self.conversations_repo.get_by_chat_id(chat_id).id
        self.conv_requests_repo.add(
            ConversationRequest(
                id=conversation_id,
                conversation_id=conversation_id,
                user_id=user_id,
                prompt=request,
                answer=answer,
            )
        )
        self.db_session.commit()
        self.logger.debug(f"The answer is:\n{answer}")
        return answer

    def logout_filters(self, message: Message):
        return (
            message.chat.id in self.chats.keys()
            and self.chats[message.chat.id].authorized
            and (
                not message.chat.is_forum
                or message.message_thread_id == self.chats[message.chat.id].thread_id
            )
        )

    async def logout(self, chat_id, user_id):
        chat = self.chats[chat_id]
        if user_id in chat.admins:
            self.chats.pop(chat_id)
            self.logger.debug("User ended conversation")
            conversation = self.conversations_repo.get_by_chat_id(chat_id)
            conversation.is_stopped = True
            self.conversations_repo.persist(conversation)
            self.db_session.commit()
            return "Goodbye! I hope I was helpful."
        else:
            return "You do not have access to stop this conversation."

    async def get_conversation_history(self, chat_id):
        conversation_id = self.conversations_repo.get_by_chat_id(chat_id).id
        return self.conversations_repo.get_conversation_requests_history(
            conversation_id
        )

    async def _list_of_conversations_to_text(
        self, list_: List[Conversation], start_count: int = 0
    ):
        convs = []
        count = 1 + start_count
        list_.sort(key=lambda c: c.created_at, reverse=True)
        for conv in list_:
            status = "В работе" if conv.is_stopped else "Остановлен"
            try:
                created_at = conv.created_at.strftime("%Y-%m-%d %H:%M")
            except AttributeError:
                created_at = conv.created_at
            convs.append(
                f"{count}. <code>Чат - {conv.chat_id} | Инициатор - {conv.created_by} "
                f"| Время создания - {created_at} "
                f"| Статус - {status} </code>| ID: <code>{conv.id}</code>"
            )
            count += 1
        return "\n".join(convs)

    async def get_conversations_pagination_text(
        self, page_number: int = 0, convs_list: Optional[List[Conversation]] = None
    ):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(
                text="<<",
                callback_data=f"convs-list-pagination_{page_number - 1}",
            ),
            InlineKeyboardButton(
                text=">>",
                callback_data=f"convs-list-pagination_{page_number + 1}",
            ),
        )
        if not convs_list:
            convs_list = self.conversations_repo.list()
        if len(convs_list) <= 20:
            return (
                await self._list_of_conversations_to_text(convs_list, page_number * 20),
                kb,
            )
        if len(convs_list) == 0:
            return "Список пока пуст", kb
        else:
            if (len(convs_list) - 20 * page_number) < 20:
                stop = len(convs_list)
            else:
                stop = 20 * page_number + 20
            return (
                await self._list_of_conversations_to_text(
                    convs_list[(20 * page_number) : stop], page_number * 20
                ),
                kb,
            )
