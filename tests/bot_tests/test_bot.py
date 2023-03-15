from pyrogram.client import Client

from bot.models.users import UsersRepository
from config import config


async def test_user_registering_at_start(session, setup_bot, telegram_client: Client):
    async with telegram_client as client:
        await client.send_message(text="/start", chat_id=config.bot_name)
        users_repo = UsersRepository(session)
        assert (await client.get_me()).id in users_repo.dict()
