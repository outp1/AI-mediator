from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.controllers.chatgpt import ChatGPTController
from bot.middlewares import ObjectsTransferMiddleware
from bot.handlers.chatgpt import register_chatgpt_handlers
from config import config


def register_controllers(bot: Bot):
    bot["chatgpt_controller"] = ChatGPTController()


def register_handlers(dp: Dispatcher):
    register_chatgpt_handlers(dp, dp.bot["chatgpt_controller"])


def register_middlewares(dp: Dispatcher):
    dp.setup_middleware(ObjectsTransferMiddleware())


async def start_bot():
    bot = Bot(token=config.bot_token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=MemoryStorage())

    bot["dp"] = dp

    register_controllers(bot)
    register_handlers(dp)
    register_middlewares(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
