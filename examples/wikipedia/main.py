import json

import requests
from schema import MainEnPage

if __name__ == "__main__":
    resp = requests.get("https://en.wikipedia.org").text
    main_page_en = MainEnPage(resp)
    print(json.dumps(main_page_en.dict(), indent=4))
