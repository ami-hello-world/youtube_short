# キャラクターの越えの種類とidの一覧を表示する

import requests
from rich import print

host = "127.0.0.1"
port = "50021"


def get_speakers():
    # キャラクターの一覧を取得する
    res = requests.get(f"http://{host}:{port}/speakers")
    print(res.json())

import os
def api():
    print(os.getenv("OPENAI_API_KEY"))


if __name__ == "__main__":
    get_speakers()
    api()