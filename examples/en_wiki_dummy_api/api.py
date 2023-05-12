from typing import Union

from _http import send_request, a_send_request
from models import IS_REFER, PageContent, PageRefer
import logging
logger = logging.getLogger('scrape_schema')
logger.setLevel(logging.ERROR)


class EnWikiApi:
    def search(self, query) -> Union[PageRefer, PageContent]:
        response = send_request(f"https://en.wikipedia.org/wiki/{query}")
        if IS_REFER.search(response):
            return PageRefer(response)
        return PageContent(response)

    async def a_search(self, query) -> Union[PageRefer, PageContent]:
        response = await a_send_request(f"https://en.wikipedia.org/wiki/{query}")
        if IS_REFER.search(response):
            return PageRefer(response)
        return PageContent(response)