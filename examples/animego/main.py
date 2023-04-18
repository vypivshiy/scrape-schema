# NOTE: this example works only CIS counties
import pprint

import requests
from schema import AnimegoSchema

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
}

if __name__ == "__main__":
    response = requests.get("https://animego.org/", headers=headers).text
    schema = AnimegoSchema(response)
    pprint.pprint(schema.dict(), width=60, compact=True)
