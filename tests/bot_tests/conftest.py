import asyncio
import inspect
import json

import pytest
from aioresponses import aioresponses as aiorsp
from pyrogram.client import Client

from bot import start_bot
from bot.controllers.chatgpt import ChatGPTController
from config import config


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
def mock_request(request):
    aioresponses_ = aioresponses()
    print("mocking request")
    aioresponses_.start()
    for marker in request.node.iter_markers("mock_response"):
        params = {
            "url": None,
            "method": None,
            "status": None,
            "headers": None,
            "file": None,
        }

        params.update(marker.kwargs)

        aioresponses_.add(
            params["url"],
            params["method"],
            params["status"],
            payload=json.load(open(params["file"])),
            repeat=True,
            headers=params["headers"],
        )
    yield aioresponses_
    aioresponses_.stop()


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
