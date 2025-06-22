import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 読み込み専用API（本アカ）
bearer_token = os.getenv("TWITTER_READ_BEARER_TOKEN")
api_key = os.getenv("TWITTER_READ_API_KEY")
api_secret = os.getenv("TWITTER_READ_API_SECRET")
access_token = os.getenv("TWITTER_READ_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_READ_ACCESS_SECRET")

# Tweepy クライアント（v1.1対応）
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
api = tweepy.API(auth)

def get_trend_words(woeid=23424856, top_n=10):
    """
    WOEID = 23424856（日本）／2343972（東京）など指定可
    """
    try:
        trends_result = api.get_place_trends(id=woeid)
        trends = trends_result[0]['trends']
        words = [t['name'] for t in trends if not t['name'].startswith('#')]
        return words[:top_n]
    except Exception as e:
        print(f"[ERROR] トレンド取得失敗: {e}")
        return []

if __name__ == "__main__":
    trend_words = get_trend_words(woeid=2343972)  # 東京のトレンド
    print("[INFO] 今日のトレンド語:")
    for word in trend_words:
        print(f"- {word}")
