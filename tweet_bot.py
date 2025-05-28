import os
import time
import tweepy
from post_generator import generate_babaa_post

# 認証情報（環境変数またはGitHub Secrets）
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Tweepy v2 Client（OAuth1.0a 認証を含む）
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

def post_to_twitter(post):
    text = f"{post['text']}\n{' '.join(post['tags'])}"
    try:
        response = client.create_tweet(text=text)
        print(f"✅ 投稿成功: {response.data}")
    except Exception as e:
        print(f"❌ Twitter投稿失敗: {e}")

if __name__ == "__main__":
    count = 0
    max_posts = 5
    max_attempts = 15

    print("🔁 ババァ投稿生成中...")
    while count < max_posts and max_attempts > 0:
        post = generate_babaa_post()
        if post:
            post_to_twitter(post)
            count += 1
            time.sleep(3)  # 間隔調整（必要に応じて長く）
        else:
            print("❌ 投稿冷却／生成失敗")
        max_attempts -= 1
