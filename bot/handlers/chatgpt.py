from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import InvalidPeerID, MessageToEditNotFound

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
        message.text, message.chat.id, message.from_user.id
    )
    await message.reply(text=answer)


async def logout(message: Message, chatgpt_controller: ChatGPTController):
    answer = await chatgpt_controller.logout(message.chat.id, message.from_user.id)
    await message.answer(answer)


async def admin_actions(message: Message, chatgpt_controller: ChatGPTController):
    action, data = message.text.split(" ")[0], " ".join(message.text.split(" ")[1:])
    action = action.split("_")[1]
    if action == "conversations":
        text, keyboard = await chatgpt_controller.get_conversations_pagination_text()
        return await message.answer(text, reply_markup=keyboard)
    elif action == "gethistory":
        text = ""
        if data:
            file = await chatgpt_controller.get_conversation_history_file(int(data))
            await message.answer_document(
                file, caption=f"История разговора с ID - <code>{data}</code>"
            )
        else:
            return await message.answer(
                "Укажите через пробел ID разговора для работы команды."
            )


async def conversations_pagination(
    call: CallbackQuery, chatgpt_controller: ChatGPTController, dp: Dispatcher
):
    page_number = int(call.data.split("_")[1])
    if page_number < 0:
        page_number = 0
    text, keyboard = await chatgpt_controller.get_conversations_pagination_text(
        page_number
    )
    try:
        await dp.bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
        )
    except MessageToEditNotFound:
        await call.message.answer(text, reply_markup=keyboard)
    await call.answer()


def register_chatgpt_handlers(dp: Dispatcher, controller: ChatGPTController):
    dp.register_message_handler(start, commands=["start_gpt3"], state="*")
    dp.register_message_handler(start, text="Общаться с ChatGPT \U0001f916", state="*")

    dp.register_message_handler(login, controller.login_filters, state="*")
    dp.register_message_handler(
        logout, controller.logout_filters, commands=["stop"], state="*"
    )

    dp.register_message_handler(
        process_message, controller.process_message_filters, state="*"
    )

    dp.register_message_handler(
        admin_actions,
        lambda m: m.text.startswith("/chatgpt_"),
        is_admin=True,
        state="*",
    )
    dp.register_callback_query_handler(
        conversations_pagination,
        lambda c: c.data.startswith("convs-list-pagination_"),
        is_admin=True,
        state="*",
    )
