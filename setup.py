import logging

from aiogram import Bot, Dispatcher, executor, types

from bot.bot import TelegramChatGPTBot
from config import Config


config = Config()
print(config.__dict__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.info(config.__dict__)

# Initialize bot and dispatcher
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot)

tgbot = TelegramChatGPTBot(config.chatgpt_password, bot, dp)
tgbot.register()

# Start the Bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
