from aiogram import Dispatcher
from aiogram.types import Message

from bot.controllers.chatgpt import ChatGPTController
from bot.models.chatgpt import StartBotArgs
from bot.utils import throttle_user
from config import config


async def start(message: Message, chatgpt_controller: ChatGPTController):
    await message.reply(
        text=await chatgpt_controller.start(
            StartBotArgs(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                thread_id=message.message_thread_id if message.chat.is_forum else None,
            )
        )
    )


async def login(message: Message, chatgpt_controller: ChatGPTController):
    await message.reply(
        await chatgpt_controller.login(
            message.chat.id, message.text, message.from_user.id
        )
    )


async def process_message(
    message: Message, dp: Dispatcher, chatgpt_controller: ChatGPTController
):
    if config.chat_timeout > 0:
        throttled = await throttle_user(message, dp)
        if throttled:
            return

    answer = await chatgpt_controller.process(
        message.text, message.chat.id, message.chat.id
    )
    await message.reply(text=answer)


async def logout(message: Message, chatgpt_controller: ChatGPTController):
    answer = await chatgpt_controller.logout(message.chat.id, message.from_user.id)
    await message.answer(answer)


def register_chatgpt_handlers(dp: Dispatcher, controller: ChatGPTController):
    dp.register_message_handler(start, commands=["start_conv"], state="*")

    dp.register_message_handler(login, controller.login_filters, state="*")
    dp.register_message_handler(
        logout, controller.logout_filters, commands=["stop"], state="*"
    )

    dp.register_message_handler(
        process_message, controller.process_message_filters, state="*"
    )
