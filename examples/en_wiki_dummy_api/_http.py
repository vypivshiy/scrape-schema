from httpx import AsyncClient, Client

__all__ = ["send_request", "a_send_request"]


def send_request(url: str) -> str:
    return Client(follow_redirects=True).get(url).text


async def a_send_request(url: str) -> str:
    async with AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)
        return response.text
