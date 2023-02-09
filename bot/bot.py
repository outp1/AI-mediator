import random
from typing import Optional
import logging

from aiogram import Bot, Dispatcher, dispatcher, executor, types
from aiogram.dispatcher.filters.state import State

from chat_request import OpenAIRequest


class TelegramChatGPTBotConversation:
    chat_id: Optional[int] = None
    accepted = False
    timeout = 0

    def __init__(
        self,
        password: str,
        bot: Bot,
        dispatcher: Dispatcher,
        requester: OpenAIRequest,
        admins=[],
        timeout = 0
    ):
        self.conversation_id = "".join(random.choice(list("1234567890")) for i in range(6))
        self.password = password
        self.bot = bot
        self.dispatcher = dispatcher
        self.requester = requester
        self.entering_user_id = None
        self.admins = [*admins]
        self.timeout = timeout

    async def cmd_start(self, message: types.Message):
        """
        Conversation's entry point.
        """
        if self.accepted:
            return await message.reply("Password actually accepted")
        await message.answer(text="Please enter the password")
        self.entering_user_id = message.from_user.id
        self.chat_id = message.chat.id
        if message.chat.is_forum:
            self.message_thread_id = message.message_thread_id
        else:
            self.message_thread_id = None

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
            logging.info(
                f"{message.from_user.mention} started new dialog with id {self.conversation_id}"
                f" in {message.chat.mention}"
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
        if self.timeout > 0:
            res = await self.dispatcher.throttle(
                key="chatgpt",
                rate=self.timeout,
                user_id=message.from_user.id,
                no_error=True
            )
            if res is False:
                return await message.reply(f"Подожди {self.timeout} секунд перед тем как задавать ещё один вопрос")
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
