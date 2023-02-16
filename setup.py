import logging

from aiogram import executor

from bot.views import chatgpt_dispatcher
logging.basicConfig(level="DEBUG")

if __name__ == "__main__":
    executor.start_polling(chatgpt_dispatcher, skip_updates=True)
