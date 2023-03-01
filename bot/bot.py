from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.controllers.chatgpt import ChatGPTController
from bot.views.chatgpt import register_chatgpt_views
from config import config


def register_views(dp: Dispatcher):
    register_chatgpt_views(dp)


async def start_bot():
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_views(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
