from aiogram import Bot, Dispatcher, executor, types

from chat_request import OpenAIRequest


class TelegramChatGPTBot:

    def __init__(
        self, 
        password: str, 
        bot: Bot, 
        dispatcher: Dispatcher,
        requester: OpenAIRequest
    ):
        self.password = password
        self.bot = bot
        self.dispatcher = dispatcher
        self.requester = requester

    async def cmd_start(self, message: types.Message):
        """
        Conversation's entry point.
        """
        if message.text.split(' ')[1] == self.password:
            # if password is correct, proceed to next step
            await message.answer("Password accepted, how can I help you today?")
            # set active user for further interaction
            self.user_id = message.from_user.id
        else:
            # if password is incorrect, deny access
            await message.answer("Invalid password, access denied.")

    async def cmd_stop(self, message: types.Message):
        """
        Conversation's exit point.
        """
        if message.from_user.id == self.user_id:
            await self.bot.send_message(
                chat_id=message.chat.id, 
                text='Goodbye! I hope I was helpful.'
            )
            self.user_id = None
        else:
            # if user is not active, deny access
            await message.answer("You do not have access to stop this conversation.")

    async def handle_text(self, message: types.Message):
        """
        Handle text messages
        """
        if message.from_user.id == self.user_id:
            # make API request to ChatGPT here and return the response
            response = self.requester.send_request(message.text)
            await message.answer(response)
        else:
            # if user is not active, deny access
            await message.answer("You do not have access to use this bot.")

    def register(self):
        self.dispatcher.register_message_handler(
            self.cmd_start, commands=['start'], state='*'
        )
        self.dispatcher.register_message_handler(
            self.cmd_stop, commands=['stop'], state='*'
        )
        self.dispatcher.register_message_handler(
            self.handle_text, state='*'
        )
