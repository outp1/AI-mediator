import pytest

from bot.models.chatgpt import StartBotArgs
from config import config


async def test_start(chatgpt_controller):
    result = await chatgpt_controller.start(StartBotArgs(user_id=1, chat_id=1))
    assert result == "Please enter the password"


async def test_login_success(chatgpt_controller):
    await chatgpt_controller.start(StartBotArgs(user_id=1, chat_id=1))

    result = await chatgpt_controller.login(1, config.chatgpt_password, 1)
    assert result == "Password accepted, how can I help you today?"


async def test_login_fail(chatgpt_controller):
    await chatgpt_controller.start(StartBotArgs(user_id=1, chat_id=1))

    result = await chatgpt_controller.login(1, "000", 2)
    assert result == "Invalid password, access denied."


@pytest.mark.mock_response(
    url="https://api.openai.com/v1/completions",
    method="POST",
    status=200,
    file="tests/bot_tests/test-data/test_openai_response_200.json",
)
async def test_process(mock_request, chatgpt_controller):
    result = await chatgpt_controller.process("some", disable_proxy=True)
    assert result == "Hello World"
