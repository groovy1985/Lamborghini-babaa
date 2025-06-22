import os
import json
import tweepy
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 読み込み専用API（本アカ）
bearer_token = os.getenv("TWITTER_READ_BEARER_TOKEN")
api_key = os.getenv("TWITTER_READ_API_KEY")
api_secret = os.getenv("TWITTER_READ_API_SECRET")
access_token = os.getenv("TWITTER_READ_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_READ_ACCESS_SECRET")

# Tweepy クライアント（v1.1）
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
api = tweepy.API(auth)

# 保存ディレクトリ
SAVE_DIR = "logs/trend_words"
os.makedirs(SAVE_DIR, exist_ok=True)

def get_trend_words(woeid=2343972, top_n=10):
    """
    WOEID: 2343972 = Tokyo / 23424856 = Japan
    """
    try:
        trends_result = api.get_place_trends(id=woeid)
        trends = trends_result[0]['trends']
        words = [t['name'] for t in trends if not t['name'].startswith('#')]
        return words[:top_n]
    except Exception as e:
        print(f"[ERROR] トレンド取得失敗: {e}")
        return []

def save_trend_words(words):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SAVE_DIR, f"{today}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"[INFO] トレンド語を保存: {path}")

if __name__ == "__main__":
    trend_words = get_trend_words()
    if trend_words:
        print("[INFO] 今日のトレンド語:")
        for word in trend_words:
            print(f"- {word}")
        save_trend_words(trend_words)
