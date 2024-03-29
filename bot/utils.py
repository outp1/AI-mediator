import time

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from config import config


async def throttle_user(message, dp):
    throttle_check = await dp.check_key("chatgpt", user_id=message.from_user.id)
    if throttle_check.result is False:
        await dp.throttle(
            key="chatgpt",
            no_error=True,
            user_id=message.from_user.id,
            rate=config.chat_timeout,
        )
    else:
        if throttle_check.called_at + 60 > time.time():
            await message.reply(
                f"Please wait {int(throttle_check.called_at + 60 - time.time())}"
                " seconds before making a new request."
            )
            return True
        await dp.throttle(
            key="chatgpt",
            rate=config.chat_timeout,
            user_id=message.from_user.id,
            no_error=True,
        )


def get_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="Общаться с ChatGPT \U0001f916"))
    return kb


def get_privacy_policy_keyboard(user_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="Принять", callback_data=f"privacypolicyaccept_{user_id}"
        )
    )
