import requests
import random
import time
import os

def download_random_vertical_video(filename="main.mp4") -> str | None:
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')
    print(PIXABAY_API_KEY)
    url = "https://pixabay.com/api/videos/"
    per_page = 10
    CATEGORIES = ["animals"]

    chosen_category = random.choice(CATEGORIES)

    base_params = {
        "key": PIXABAY_API_KEY,
        "video_type": "film",
        "category": chosen_category,
        "min_duration": 20,
        "max_duration": 60,
        "safesearch": "true",
        "per_page": per_page,
    }

    # 総件数を取得してページ上限を計算
    initial = requests.get(url, params={**base_params, "page": 1})
    if initial.status_code != 200:
        print(f"初回リクエスト失敗: {initial.status_code}")
        return None
    meta = initial.json()
    total_hits = meta.get("totalHits", 0)
    if total_hits == 0:
        print(f"カテゴリ '{chosen_category}' では動画が見つかりませんでした。")
        return None

    max_pages = min(50, (total_hits // per_page) + 1)

    # ランダムページから取得＆縦型動画を抽出
    for _ in range(10):  # 最大10回試行
        random_page = random.randint(1, max_pages)
        response = requests.get(url, params={**base_params, "page": random_page})
        if response.status_code != 200:
            print(f"Pixabay APIリクエスト失敗: {response.status_code}")
            return None
        data = response.json()
        hits = data.get("hits", [])
        vertical_videos = [
            v for v in hits
            if v["videos"]["medium"]["height"] > v["videos"]["medium"]["width"]
        ]
        if vertical_videos:
            video = random.choice(vertical_videos)
            video_url = video["videos"]["medium"]["url"]
            video_data = requests.get(video_url)
            if video_data.status_code != 200:
                print(f"動画のダウンロード失敗: {video_data.status_code}")
                return None
            with open(filename, "wb") as f:
                f.write(video_data.content)
            time.sleep(1)
            print(f"✅ カテゴリ '{chosen_category}' の動画を保存しました: {filename}")
            return filename

    print(f"カテゴリ '{chosen_category}' で縦型動画が見つかりませんでした。")
    return None

if __name__ == "__main__":
    download_random_vertical_video(filename="main.mp4")