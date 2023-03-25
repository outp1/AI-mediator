import asyncio
import time

from pyrogram.client import Client
from pyrogram.types import Message

from bot.models.users import UsersRepository
from config import config

MAX_WAIT = 10


def wait(fn):
    async def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return await fn(*args, **kwargs)
            except AssertionError as exc:
                if time.time() - start_time >= MAX_WAIT:
                    raise exc
                time.sleep(0.5)

    return modified_fn


async def get_last_message(client, chat_name) -> Message:
    async for message in client.get_chat_history(chat_name, limit=1):
        return message


@wait
async def assert_last_messsage_text_in(client, chat_name, text):
    last_message = await get_last_message(client, chat_name)
    if last_message:
        if getattr(last_message, "text"):
            assert text in last_message.text
        elif getattr(last_message, "caption"):
            assert text in last_message.caption
        else:
            raise AssertionError
        return
    raise AssertionError


async def test_user_registering_at_start(session, telegram_client: Client):
    async with telegram_client as client:
        await client.send_message(text="/start", chat_id=config.bot_name)
        await assert_last_messsage_text_in(client, config.bot_name, "Приветствую")
        users_repo = UsersRepository(session)
        assert (await client.get_me()).id in users_repo.dict()


async def test_admin_filter(telegram_client: Client):
    async with telegram_client as client:
        user_id = (await client.get_me()).id

        admins = config.admins
        try:
            config.admins = [user_id]
            await client.send_message(config.bot_name, "/admin")
            await assert_last_messsage_text_in(
                client, config.bot_name, "Вы администратор"
            )

            config.admins = []
            await client.send_message(config.bot_name, "/admin")
            await asyncio.sleep(2)
            await assert_last_messsage_text_in(client, config.bot_name, "/admin")
        finally:
            config.admins = admins
