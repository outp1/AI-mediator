import datetime
import json
import time
from io import BytesIO
from typing import Optional

from pyrogram.client import Client
from pyrogram.types import Message
from sqlalchemy.orm import Session

from bot.controllers.bot import MenuController
from bot.models import ConversationsRepository
from bot.models.chatgpt import (
    Conversation,
    ConversationRequest,
    ConversationRequestsRepository,
)
from bot.models.users import User, UsersRepository
from config import config
from utils.id_generator import generate_base_id

MAX_WAIT = 10


def wait(fn):
    async def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return await fn(*args, **kwargs)
            except AssertionError as exc:
                if time.time() - start_time >= MAX_WAIT:
                    raise exc
                time.sleep(0.5)

    return modified_fn


async def get_last_message(client, chat_name) -> Optional[Message]:
    async for message in client.get_chat_history(chat_name, limit=1):
        return message


@wait
async def assert_last_messsage_text_in(client, chat_name, text):
    last_message = await get_last_message(client, chat_name)
    if last_message:
        if getattr(last_message, "text"):
            assert text in last_message.text
        elif getattr(last_message, "caption"):
            assert text in last_message.caption
        else:
            raise AssertionError
        return
    raise AssertionError


def register_test_user(session, user_id=None):
    users_repo = UsersRepository(session)
    if not user_id:
        user_id = generate_base_id()
    user = User(id=user_id, username="test")
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


async def login_conversation_in_direct(client: Client, menu_controller: MenuController):
    data = await client.get_me()
    await menu_controller.register_user(User(id=data.id, username=data.mention))

    await client.send_message(config.bot_name, "/start_gpt3")
    await assert_last_messsage_text_in(
        client, config.bot_name, "Здравствуйте, я ChatGPT 3"
    )


async def test_chatgpt_login(
    telegram_client: Client, session, menu_controller: MenuController
):
    async with telegram_client as client:
        await login_conversation_in_direct(client, menu_controller)

        assert len(ConversationsRepository(session).list()) == 1


async def test_chatgpt_processing(
    aioresponses, telegram_client: Client, menu_controller: MenuController, session
):
    aioresponses.post(
        config.openai_url,
        payload=json.load(
            open("tests/bot_tests/test-data/test_openai_response_200.json")
        ),
        status=200,
        repeat=True,
    )
    async with telegram_client as client:
        user_id = (await client.get_me()).id
        register_test_user(session, user_id)
        await login_conversation_in_direct(client, menu_controller)
        await client.send_message(config.bot_name, "Hello")
        await assert_last_messsage_text_in(client, config.bot_name, "Hello World")


async def test_chatgpt_logout(
    telegram_client: Client,
    menu_controller,
    session: Session,
):
    async with telegram_client as client:
        await login_conversation_in_direct(client, menu_controller)
        await client.send_message(config.bot_name, "/stop")
        await assert_last_messsage_text_in(client, config.bot_name, "Goodbye!")

        chat_id = (await client.get_me()).id
        repo = ConversationsRepository(session)
        assert repo.get_by_chat_id(chat_id, is_stopped=True)


async def test_conversations_list_pagination(telegram_client: Client, session):
    async with telegram_client as client:
        user = await client.get_me()
        list_ = list(
            {
                "id": generate_base_id(),
                "chat_id": generate_base_id(),
                "is_stopped": False,
                "created_at": datetime.datetime.now(),
                "created_by": user.id,
            }
            for i in range(50)
        )
        users_repo = UsersRepository(session)
        users_repo.add(User(id=user.id, username=user.username))
        session.commit()

        convs_repo = ConversationsRepository(session)
        for conv in list_:
            convs_repo.add(Conversation(**conv))
        session.commit()

        await client.send_message(config.bot_name, "/chatgpt_conversations")
        await assert_last_messsage_text_in(client, config.bot_name, "1. Чат")
        msg = await get_last_message(client, config.bot_name)
        await msg.click(1)
        await assert_last_messsage_text_in(client, config.bot_name, "21. Чат")


async def test_convesation_history_getting(telegram_client: Client, session):
    async with telegram_client as client:
        user = register_test_user(session)
        conv = register_test_conversation(session, user.id)

        requests_repo = ConversationRequestsRepository(session)
        requests_repo.add(
            ConversationRequest(
                id=generate_base_id(),
                conversation_id=conv.id,
                user_id=user.id,
                prompt="Hello",
                answer="Hello World",
            )
        )
        requests_repo.add(
            ConversationRequest(
                id=generate_base_id(),
                conversation_id=conv.id,
                user_id=user.id,
                prompt="Bye",
                answer="Bye, darling",
            )
        )
        session.commit()

        await client.send_message(config.bot_name, f"/chatgpt_gethistory {conv.id}")
        await assert_last_messsage_text_in(
            client, config.bot_name, f"История разговора с ID "
        )
        msg = await get_last_message(client, config.bot_name)
        file = await client.download_media(msg, in_memory=True)

        assert type(file) is BytesIO
        result = json.loads(file.getvalue().decode())

        assert len(result) == 2
        assert result[0]["conversation_id"] == conv.id
