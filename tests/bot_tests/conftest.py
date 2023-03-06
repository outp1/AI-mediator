import asyncio
import inspect

import pytest
from aioresponses import aioresponses as aiorsp
from pyrogram.client import Client

from bot import start_bot
from bot.controllers.chatgpt import ChatGPTController
from config import config
from logging_conf import prepare_logging

prepare_logging()


@pytest.fixture
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


def pytest_collection_modifyitems(config, items):
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


@pytest.fixture
def aioresponses():
    with aiorsp(passthrough_unmatched=True) as aior:
        yield aior


@pytest.fixture
def chatgpt_controller():
    yield ChatGPTController()


@pytest.fixture
def setup_bot(event_loop):
    event_loop.create_task(start_bot())
    yield


@pytest.fixture
def telegram_client(setup_bot):
    client = Client(
        "test-data.test_client",
        api_id=config.tests.api_id,
        api_hash=config.tests.api_hash,
    )
    yield client
