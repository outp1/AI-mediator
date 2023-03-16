from bot.models.chatgpt import (Conversation, ConversationRequestsHistory,
                                ConversationsRepository)
from bot.models.users import User, UsersRepository
from utils.id_generator import generate_base_id

# TODO: tests should test only one unit of module, need refactor


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


def test_conversations_repository(session):
    repository = ConversationsRepository(session)
    users_repository = UsersRepository(session)

    user = User(id=generate_base_id(users_repository.get_by_id), username="test")
    users_repository.add(user)

    conversation = Conversation(
        id=generate_base_id(repository.get_by_id), chat_id=123456, created_by=user.id
    )

    # Can add
    repository.add(conversation)
    assert repository.get_by_id(conversation.id) == conversation

    # Can persist
    conversation.chat_id = 141414
    repository.persist(conversation)
    assert repository.get_by_id(conversation.id).chat_id == conversation.chat_id

    # Can take list
    conversation2 = Conversation(
        id=generate_base_id(repository.get_by_id), chat_id=141451, created_by=user.id
    )
    repository.add(conversation2)
    list_ = repository.list()
    assert len(list_) == 2
    assert type(list_[1]) is Conversation

    # Can persist many
    repository._identity_map["conversations"][conversation2.id].chat_id = 616616
    repository.persist_all()
    assert repository.get_by_id(conversation2.id).chat_id == 616616

    # Can remove
    repository.remove(conversation2)
    assert len(repository.list()) == 1

    # Can take requests history
    conv_history = repository.get_conversation_requests_history(conversation.id)
    assert type(conv_history) is ConversationRequestsHistory


# TODO: Tests for other repos. Would be advisably to create the template
#       for generate each other test
