import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.controllers.chatgpt import ChatGPTController
from bot.handlers.chatgpt import register_chatgpt_handlers
from bot.middlewares import ObjectsTransferMiddleware
from config import config
from logging_conf import prepare_logging

logger = logging.getLogger("telegram_bot")


def register_controllers(bot: Bot):
    logger.debug("Registering controllers.")
    bot["chatgpt_controller"] = ChatGPTController()


def register_handlers(dp: Dispatcher):
    logger.debug("Registering handlers.")
    register_chatgpt_handlers(dp, dp.bot["chatgpt_controller"])


def register_middlewares(dp: Dispatcher):
    logger.debug("Registering middlewares.")
    dp.setup_middleware(ObjectsTransferMiddleware())


async def start_bot():
    logger.debug("Telegram bot setup has started.")

    bot = Bot(token=config.bot_token, parse_mode="HTML")
    dp = Dispatcher(bot, storage=MemoryStorage())

    bot["dp"] = dp

    register_controllers(bot)
    register_handlers(dp)
    register_middlewares(dp)

    logger.debug("Telegram bot setup was completed successfully.")

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
