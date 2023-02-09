import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.bot import TelegramChatGPTBotConversation
from config import Config
from chat_request import OpenAIRequest


config = Config()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.bot_token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

requester = OpenAIRequest(config, config.chatgpt_api_key)

conversations = []

async def default_handler(message: types.Message):
    chat =  TelegramChatGPTBotConversation(
        password = config.chatgpt_password,
        bot = bot,
        dispatcher=dp,
        requester=requester,
        timeout=60
    )
    logging.debug(
        f"{message.from_user.mention} are attempting to start"
        f" new dialog with {chat.conversation_id} id in {message.chat.mention}"
    )
    await chat.cmd_start(message)
    chat.register()
    conversations.append(chat)

dp.register_message_handler(default_handler, commands=["start_conv"], state="*")

#tgbot = TelegramChatGPTBotConversation(
#    config.chatgpt_password, bot, dp, requester, timeout=60
#)
#tgbot.register()

# Start the Bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
