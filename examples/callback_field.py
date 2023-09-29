# mypy: disable-error-code="assignment"
"""Your best friend for write Callback fields:
- itertools
- functools.partial
- lambda functions
"""
import random
from functools import partial
from itertools import count
from string import ascii_lowercase
from uuid import uuid4

from scrape_schema import BaseSchema, Callback


def _random_word(len_=16) -> str:
    return "".join(random.choices(population=ascii_lowercase, k=len_))


# create a simple counter
counter = count(1)
my_counter = partial(lambda: next(counter))


# also you can create alias field
FieldUUID4 = Callback(lambda: str(uuid4()))


class CallbackSchema(BaseSchema):
    num: int = Callback(my_counter)
    # not need init alias. same as uuid argument
    uuid: str = FieldUUID4
    # same as
    # uuid: str = Callback(lambda: str(uuid4()))

    word: str = Callback(_random_word)
    # also Callback field support SpecialMethod functions
    long_word: str = Callback(partial(_random_word, 32)).concat_l("LONG: ")


print(CallbackSchema("").dict())
print(CallbackSchema("").dict())
print(CallbackSchema("").dict())
# {'num': 1, 'uuid': 'a6b5be7a-1f6e-4f37-bfc3-9cfba36ed9f0', 'word': 'lftxzhxsfktwxrzs',
# 'long_word': 'LONG: begxplujskfeeriivqqbdbqakcfnlvtm'}
# {'num': 2, 'uuid': 'b41de697-4c73-4f08-9d53-4c62adc3e506', 'word': 'ylkdunpqxvyevzzf',
# 'long_word': 'LONG: uvtllkxetatsrsqwauiovqpbwiqvswoh'}
# {'num': 3, 'uuid': '457c7ecc-adbe-447e-b914-9a5e3c22af7a', 'word': 'zjrtgxtaraihhngw',
# 'long_word': 'LONG: wzsjvqcvwyydqgiichhohtwagzlajter'}
