import inspect
import json
import os

import pytest
from aioresponses import aioresponses

from bot.controllers.chatgpt import ChatGPTController


def pytest_collection_modifyitems(config, items):
    for item in items:
        if inspect.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


aioresponses = aioresponses()


@pytest.fixture
def mock_request(request):
    print("mocking request")
    aioresponses.start()
    for marker in request.node.iter_markers("mock_response"):
        params = {
            "url": None,
            "method": None,
            "status": None,
            "headers": None,
            "file": None,
        }

        params.update(marker.kwargs)
        params.update(
            {
                key: value
                for key, value in zip(
                    [i for i, j in params.items() if j is None], marker.args
                )
            }
        )

        aioresponses.add(
            params["url"],
            params["method"],
            params["status"],
            payload=json.load(open(params["file"])),
            repeat=True,
            headers=params["headers"],
        )
    yield
    aioresponses.stop()


@pytest.fixture()
def chatgpt_controller():
    yield ChatGPTController()
