import pytest

from bot.repos.chatgpt import OpenAIRepo


@pytest.mark.mock_response(
    url="https://api.openai.com/v1/completions",
    method="POST",
    status=200,
    file="tests/bot_tests/test-data/test_openai_response_200.json",
)
async def test_chatgpt_send_request(mock_request):
    repo = OpenAIRepo()
    result = await repo.send_request("hello openai", disable_proxy=True)
    assert result == "Hello World"


@pytest.mark.mock_response(
    url="https://api.openai.com/v1/completions",
    method="POST",
    status=401,
    file="tests/bot_tests/test-data/test_openai_response_200.json",
)
async def test_chatgpt_send_request_status_code_error(mock_request):
    repo = OpenAIRepo()
    result = await repo.send_request("hello openai", disable_proxy=True)
    assert result == "failed to get response with status code: 401"
