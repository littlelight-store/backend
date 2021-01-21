import random
import typing as t
import uuid
from decimal import Decimal
from itertools import islice
from random import randint
from string import ascii_uppercase


def generate_random_id() -> t.Type[int]:
    return randint(1, 66520)


def generate_random_price() -> Decimal:
    return Decimal(randint(10, 200))


def random_guid():
    return str(uuid.uuid4())


def random_chars(size, chars=ascii_uppercase):
    selection = iter(lambda: random.choice(chars), object())
    while True:
        yield ''.join(islice(selection, size))
