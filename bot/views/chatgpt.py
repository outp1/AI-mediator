from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message

from bot.controllers.chatgpt import ChatGPTController
from bot.models.chatgpt import StartBotArgs
from bot.utils import throttle_user
from config import config

bot = Bot(token=config.bot_token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
controller = ChatGPTController()


@dp.message_handler(commands=["start_conv"], state="*")
async def start(message: Message):
    await message.reply(
        text=await controller.start(
            StartBotArgs(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                thread_id=message.message_thread_id if message.chat.is_forum else None,
            )
        )
    )


@dp.message_handler(controller.login_filters, state="*")
async def login(message: Message):
    await message.reply(
        await controller.login(message.chat.id, message.text, message.from_user.id)
    )


@dp.message_handler(controller.process_message_filters, state="*")
async def process_message(message: Message):
    if config.chat_timeout > 0:
        throttled = await throttle_user(message, dp)
        if throttled:
            return

    answer = await controller.process(message.text)
    await message.reply(text=answer)


@dp.message_handler(controller.process_message_filters, commands=["stop"], state="*")
async def logout(message: Message):
    answer = await controller.logout(message.chat.id, message.from_user.id)
    await message.answer(answer)
