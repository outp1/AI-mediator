import json
from io import TextIOWrapper

from sqlalchemy.orm import Session

from bot.controllers.chatgpt import ChatGPTController
from bot.models.chatgpt import Chat, Conversation, ConversationsRepository, StartBotArgs
from bot.models.users import User, UsersRepository
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


async def test_conversation_history_file_getting(
    aioresponses, chatgpt_controller: ChatGPTController, session: Session
):
    aioresponses.post(
        url="https://api.openai.com/v1/completions",
        status=200,
        payload=json.load(
            open("tests/bot_tests/test-data/test_openai_response_200.json")
        ),
        repeat=True,
    )

    # login conversation
    users_repo = UsersRepository(session)
    user_id = generate_base_id()
    users_repo.add(User(id=user_id, username="user"))
    session.commit()
    convs_repo = ConversationsRepository(session)
    conv = Conversation(id=generate_base_id(), chat_id=user_id, created_by=user_id)
    convs_repo.add(conv)
    session.commit()
    chatgpt_controller.chats[conv.chat_id] = Chat(
        conv.chat_id, conv.thread_id, True, [conv.created_by], conv.created_by
    )

    await chatgpt_controller.process("Hello", user_id, user_id)
    await chatgpt_controller.process("Hello", user_id, user_id)

    conv = convs_repo.get_by_chat_id(user_id).id

    file = await chatgpt_controller.get_conversation_history_file(conv)

    assert len(json.load(file)) == 2
