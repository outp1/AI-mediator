import time

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

    return throttle_check.result
