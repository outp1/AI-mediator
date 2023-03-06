import json

import pytest

from bot.repos.chatgpt import OpenAIRepo


async def test_chatgpt_send_request(aioresponses):
    repo = OpenAIRepo()
    aioresponses.post(
        url="https://api.openai.com/v1/completions",
        status=200,
        payload=json.load(
            open("tests/bot_tests/test-data/test_openai_response_200.json")
        ),
    )
    result = await repo.send_request("hello openai", disable_proxy=True)
    assert result == "Hello World"


async def test_chatgpt_send_request_status_code_error(aioresponses):
    repo = OpenAIRepo()
    aioresponses.post(url="https://api.openai.com/v1/completions", status=401)
    result = await repo.send_request("hello openai", disable_proxy=True)
    assert result == "failed to get response with status code: 401"
