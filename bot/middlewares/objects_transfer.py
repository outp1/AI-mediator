import sys

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware


class ObjectsTransferMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        data["dp"] = obj.bot.get("dp")

        # repos
        data["chatgpt_controller"] = obj.bot.get("chatgpt_controller")
