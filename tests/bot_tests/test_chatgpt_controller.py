import json

from sqlalchemy.orm import Session

from bot.controllers.chatgpt import ChatGPTController
from bot.models.chatgpt import Conversation, ConversationsRepository, StartBotArgs
from bot.models.users import User, UsersRepository
from config import config
from utils.id_generator import generate_base_id


def register_test_user(session, user_id=generate_base_id(), username="test"):
    users_repo = UsersRepository(session)
    user = User(id=user_id, username=username)
    users_repo.add(user)
    session.commit()
    return user


def register_test_conversation(session, created_by):
    conv_repo = ConversationsRepository(session)
    conv = Conversation(
        id=generate_base_id(), chat_id=created_by, created_by=created_by
    )
    conv_repo.add(conv)
    session.commit()
    return conv


async def test_start(chatgpt_controller, session):
    user = register_test_user(session)
    result = await chatgpt_controller.start(
        StartBotArgs(user_id=user.id, chat_id=user.id)
    )
    assert "Здравствуйте, я ChatGPT 3" in result


async def test_login_success(chatgpt_controller, session):
    user_id = register_test_user(session).id
    register_test_conversation(session, user_id)

    await chatgpt_controller.start(StartBotArgs(user_id=user_id, chat_id=user_id))

    result = await chatgpt_controller.login(user_id, user_id)
    assert "Здравствуйте, я ChatGPT 3" in result


async def test_process(aioresponses, chatgpt_controller, session):
    aioresponses.post(
        url="https://api.openai.com/v1/completions",
        status=200,
        payload=json.load(
            open("tests/bot_tests/test-data/test_openai_response_200.json")
        ),
    )

    user_id = register_test_user(session).id
    register_test_conversation(session, user_id)

    result = await chatgpt_controller.process(
        "some", chat_id=user_id, user_id=user_id, disable_proxy=True
    )
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

    user_id = register_test_user(session).id
    conv = register_test_conversation(session, user_id)

    await chatgpt_controller.process("Hello", user_id, user_id)
    await chatgpt_controller.process("Hello", user_id, user_id)

    file = await chatgpt_controller.get_conversation_history_file(conv.id)
    result = json.load(file)
    assert len(result) == 2
    assert result[0]["answer"] == "Hello World"


async def test_two_users_cannot_start_two_convs_in_same_chat(
    chatgpt_controller: ChatGPTController, session: Session
):
    user1 = register_test_user(session)
    user2 = register_test_user(session, 456, "test2")
    await chatgpt_controller.start(StartBotArgs(user1.id, 321))
    result = await chatgpt_controller.start(StartBotArgs(user2.id, 321))

    assert "Вы уже разговариваете с ChatGPT 3" in result
