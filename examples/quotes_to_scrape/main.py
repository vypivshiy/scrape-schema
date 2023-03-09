import json
import requests
from schema import QuotePage

if __name__ == '__main__':
    resp = requests.get("https://quotes.toscrape.com/page/1/").text
    schema = QuotePage(resp)
    print(json.dumps(schema.dict(), indent=4))