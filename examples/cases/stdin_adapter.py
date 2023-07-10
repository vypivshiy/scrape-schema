import json
import sys

from schema import MainPage

if __name__ == "__main__":
    data = sys.stdin.read()
    print(json.dumps(MainPage(data).dict()))
    exit(0)
