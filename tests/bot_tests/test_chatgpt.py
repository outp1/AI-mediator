import time
import json

from pyrogram.client import Client
from pyrogram.types import Message

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


async def login_conversation(client: Client):
    await client.send_message(config.bot_name, "/start_conv")
    await assert_last_messsage_text_in(
        client, config.bot_name, "Please enter the password"
    )
    await client.send_message(config.bot_name, config.chatgpt_passwords[0])


async def test_chatgpt_login(telegram_client: Client):
    async with telegram_client as client:
        await login_conversation(client)
        await assert_last_messsage_text_in(client, config.bot_name, "Password accepted")


async def test_chatgpt_processing(aioresponses, telegram_client: Client):
    aioresponses.post(
        "https://api.openai.com/v1/completions",
        payload=json.load(
            open("tests/bot_tests/test-data/test_openai_response_200.json")
        ),
        status=200,
        repeat=True,
    )
    async with telegram_client as client:
        await login_conversation(client)
        await client.send_message(config.bot_name, "Hello")
        await assert_last_messsage_text_in(client, config.bot_name, "Hello World")
