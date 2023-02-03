from typing import Optional

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State

from chat_request import OpenAIRequest


class TelegramChatGPTBotConversation:
    chat_id: Optional[int] = None
    accepted = False

    def __init__(
        self,
        password: str,
        bot: Bot,
        dispatcher: Dispatcher,
        requester: OpenAIRequest,
        admins=[],
    ):
        self.password = password
        self.bot = bot
        self.dispatcher = dispatcher
        self.requester = requester
        self.entering_user_id = None
        self.admins = [*admins]

    async def cmd_start(self, message: types.Message):
        """
        Conversation's entry point.
        """
        await message.answer(text="Please enter the password")
        self.entering_user_id = message.from_user.id
        self.chat_id = message.chat.id
        if message.chat.is_forum:
            self.message_thread_id = message.message_thread_id

    async def cmd_stop(self, message: types.Message):
        """
        Conversation's exit point.
        """
        if message.from_user.id in self.admins:
            self.accepted = False
            await self.bot.send_message(
                chat_id=message.chat.id,
                text="Goodbye! I hope I was helpful.",
                message_thread_id=self.message_thread_id,
            )
        else:
            # if user is not active, deny access
            await message.answer("You do not have access to stop this conversation.")

    async def handle_password(self, message: types.Message):
        """
        Handle password message
        """
        if message.text == self.password:
            self.accepted = True
            self.admins.append(self.entering_user_id)
            self.entering_user_id = None
            await self.bot.send_message(
                chat_id=self.chat_id,
                message_thread_id=self.message_thread_id,
                text="Password accepted, how can I help you today?",
            )
        else:
            await message.answer("Invalid password, access denied.")
            self.entering_user_id = None

    async def handle_text(self, message: types.Message):
        """
        Handle text messages
        """
        if message.text.startswith("!"):
            return  # option to send message and not to trigger bot
        if message.chat.id == self.chat_id:
            # make API request to ChatGPT here and return the response
            answer = self.requester.send_request(
                message.text, user=message.from_user.id
            )
            await message.reply(answer)
        else:
            # if user is not active, deny access
            await message.answer("You do not have access to use this bot.")

    def register(self):
        self.dispatcher.register_message_handler(
            self.cmd_start, commands=["start_conv"], state="*"
        )
        self.dispatcher.register_message_handler(
            self.handle_password,
            lambda m: m.from_user.id == self.entering_user_id,
        )
        self.dispatcher.register_message_handler(
            self.handle_text,
            lambda m: m.chat.id == self.chat_id
            and (not m.chat.is_forum or m.message_thread_id == self.message_thread_id)
            and self.accepted
            and not m.text.startswith("/"),
            state="*",
        )
        self.dispatcher.register_message_handler(
            self.cmd_stop,
            lambda m: m.chat.id == self.chat_id
            and self.accepted
            and (not m.chat.is_forum or m.message_thread_id == self.message_thread_id),
            commands=["stop"],
            state="*",
        )
