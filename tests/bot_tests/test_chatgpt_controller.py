import json

from bot.controllers.chatgpt import ChatGPTController

from bot.models.chatgpt import Conversation, ConversationsRepository, StartBotArgs
from config import config
from utils.id_generator import generate_base_id


async def test_start(chatgpt_controller):
    result = await chatgpt_controller.start(StartBotArgs(user_id=1, chat_id=1))
    assert result == "Please enter the password"


async def test_login_success(chatgpt_controller):
    await chatgpt_controller.start(StartBotArgs(user_id=1, chat_id=1))

    result = await chatgpt_controller.login(1, config.chatgpt_passwords[0], 1)
    assert result == "Password accepted, how can I help you today?"


async def test_login_fail(chatgpt_controller):
    await chatgpt_controller.start(StartBotArgs(user_id=1, chat_id=1))

    result = await chatgpt_controller.login(1, "000", 2)
    assert result == "Invalid password, access denied."


async def test_process(aioresponses, chatgpt_controller):
    aioresponses.post(
        url="https://api.openai.com/v1/completions",
        status=200,
        payload=json.load(
            open("tests/bot_tests/test-data/test_openai_response_200.json")
        ),
    )
    result = await chatgpt_controller.process("some", disable_proxy=True)
    assert result == "Hello World"


async def test_conversations_pagination(chatgpt_controller: ChatGPTController):
    convs = json.load(
        open("tests/bot_tests/test-data/test_convesations_pagination.json")
    )["chats"]
    list_ = []
    for c in convs:
        list_.append(Conversation(id=generate_base_id(), **c))

    result = await chatgpt_controller.get_conversations_pagination_text(1, list_)

    assert str(list_[20].id) in result[0] and str(list_[39].id) in result[0]
    assert str(list_[19].id) not in result[0] and str(list_[40].id) not in result[0]

    result = await chatgpt_controller.get_conversations_pagination_text(2, list_)
    assert str(list_[40].id) in result[0] and str(list_[49].id) in result[0]
    assert str(list_[39].id) not in result[0]
