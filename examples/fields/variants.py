from typing import Annotated, Optional
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch


class Schema(BaseSchema):
    digit: Annotated[Optional[int], (ReMatch(r'spam=(\d+)'),
                                     ReMatch(r'egg=(\d+)')
                                     )]

    word: Annotated[Optional[str], (ReMatch(r'egg=([a-z]+)'),
                                    ReMatch(r'spam=([a-z]+)'))]


if __name__ == '__main__':
    print(Schema("egg=100\nspam=lorem").dict())
    # {'digit': 100, 'word': 'lorem'}
