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
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())

requester = OpenAIRequest(config, config.chatgpt_api_key)

tgbot = TelegramChatGPTBotConversation(
    config.chatgpt_password, bot, dp, requester, timeout=60
)
tgbot.register()

# Start the Bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
