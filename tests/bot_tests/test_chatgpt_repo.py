import json

import pytest

from bot.repos.chatgpt import OpenAIRepo
from config import config


async def test_chatgpt_send_request(aioresponses):
    repo = OpenAIRepo()
    aioresponses.post(
        url=config.openai_url,
        status=200,
        payload=json.load(
            open("tests/bot_tests/test-data/test_openai_response_200.json")
        ),
    )
    async with repo:
        result = await repo.send_request("hello openai", disable_proxy=True)
    assert result == "Hello World"


async def test_chatgpt_send_request_status_code_error(aioresponses):
    repo = OpenAIRepo()
    aioresponses.post(url=config.openai_url, status=401)
    async with repo:
        result = await repo.send_request("hello openai", disable_proxy=True)
    assert result == "failed to get response with status code: 401"
