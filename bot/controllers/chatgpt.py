from typing import Dict

from aiogram.types import Message

from bot.models.chatgpt import StartBotArgs, ChatModel
from bot.repos.chatgpt import OpenAIRepo
from config import config


class ChatGPTController:
    def __init__(self):
        self.chats: Dict[int, ChatModel] = {}
        self.repo = OpenAIRepo()

    async def start(self, args: StartBotArgs):
        if args.chat_id not in self.chats.keys() or self.chats[args.chat_id].authorized:
            return "Password actually accepted"
        chat = ChatModel(
            chat_id=args.chat_id,
            thread_id=args.thread_id,
            authorized=False,
            admins=[],
            entering_user_id=args.user_id,
        )
        self.chats[args.chat_id] = chat
        return "Please enter the password"

    def login_filters(self, message: Message):
        return (
            message.chat.id in self.chats.keys()
            and message.from_user.id == self.chats[message.chat.id].entering_user_id
        )

    async def login(self, chat_id, password, user_id):
        chat = self.chats[chat_id]
        result = "Invalid password, access denied."
        if password == config.chatgpt_password and user_id == chat.entering_user_id:
            chat.accepted = True
            chat.admins.append(user_id)
            chat.entering_user_id = None
            self.chats[chat_id] = chat
            result = "Password accepted, how can I help you today?"
        else:
            chat.entering_user_id = None

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

    async def process(self, request: str):
        return await self.repo.send_request(request)

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
            return "Goodbye! I hope I was helpful."
        else:
            return "You do not have access to stop this conversation."
