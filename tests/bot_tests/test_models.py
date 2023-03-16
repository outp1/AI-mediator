from bot.models.orm.users import UserModel
from bot.models.users import User, UsersRepository
from utils.id_generator import generate_base_id


def test_users_repository(session):
    repository = UsersRepository(session)
    user = User(id=generate_base_id(repository.get_by_id), username="test")

    # Can add
    repository.add(user)
    assert repository.get_by_id(user.id) == user

    # Can persist
    user.username = "another"
    repository.persist(user)
    assert repository.get_by_id(user.id).username == user.username

    # Can take list
    user2 = User(id=generate_base_id(repository.get_by_id), username="test2")
    repository.add(user2)
    list_ = repository.list()
    assert len(list_) == 2
    assert type(list_[1]) is User

    # Can persist many
    repository._identity_map["users"][user2.id].username = "another2"
    repository.persist_all()
    assert repository.get_by_id(user2.id).username == "another2"

    # Can remove
    repository.remove(user2)
    assert len(repository.list()) == 1
