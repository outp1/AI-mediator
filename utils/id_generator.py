import random

from bot.models.orm.base import BaseID


def generate_base_id(conn_func=None) -> BaseID:
    return int(_generate_id(conn_func=conn_func))


def _generate_id(len_: int = 6, conn_func=None, char_set: str = "1234567890"):
    """Returns a random number of the specified length

    Accepts a function to check if the id in the table matches and iterates until
    it creates a unique id

    """
    while True:
        number = "".join(random.choice(list(char_set)) for i in range(len_))
        if conn_func is None:
            return number
        check = conn_func(number)
        if not check:
            break
    return number
