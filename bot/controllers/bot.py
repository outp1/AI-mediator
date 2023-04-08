from sqlalchemy.orm import Session

from bot.models.users import User, UsersRepository
from bot.utils import get_menu_keyboard


class MenuController:
    def __init__(self, session: Session, db_repository: dict):
        self.session = session
        self.db_repository = db_repository
        self.users_repo = UsersRepository(session, db_repository)

    async def register_user(self, user: User):
        if not self.users_repo.get_by_id(user.id):
            self.users_repo.add(user)
            self.session.commit()

    async def get_start_data(self):
        text = (
            f"<b>\U0001f44b Приветствую! Я чат-бот, который познакомит тебя с ИИ. </b>"
            "\n\nВведи /start_gpt3 для того чтобы начать со мной диалог, "
            "либо выбери действие по кнопке в меню."
        )
        return text, get_menu_keyboard()

    async def get_user_info(self, user_id):
        return self.users_repo.get_by_id(user_id)
