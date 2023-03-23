import asyncio

from bot import start_bot
from logging_conf import prepare_logging

prepare_logging()

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass
