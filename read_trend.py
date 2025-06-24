# read_trend.py - trends24.inから日本のトレンドを取得（API不要）
import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

SAVE_DIR = "logs/trend_words"
os.makedirs(SAVE_DIR, exist_ok=True)

def get_japan_trends(top_n=10):
    url = "https://trends24.in/japan/"
    headers = {"User-Agent": "Mozilla/5.0"}  # スクレイピング対策回避
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"トレンド取得失敗: {res.status_code}")
    soup = BeautifulSoup(res.text, 'html.parser')
    trends = [tag.text.strip() for tag in soup.select("ol.trend-card__list li a")]
    return trends[:top_n]

def save_trend_words(words):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SAVE_DIR, f"{today}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"[INFO] トレンド語を保存: {path}")

if __name__ == "__main__":
    try:
        trend_words = get_japan_trends()
        print("[INFO] 今日のトレンド語:")
        for word in trend_words:
            print(f"- {word}")
        save_trend_words(trend_words)
    except Exception as e:
        print(f"[ERROR] {e}")
