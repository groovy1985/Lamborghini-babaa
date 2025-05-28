import os
import time
import tweepy
from post_generator import generate_babaa_post

# 認証情報（.env または GitHub Secrets）
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# v2 クライアント初期化（これが重要）
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
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
            try:
                post_to_twitter(post)
                count += 1
                time.sleep(3)
            except Exception as e:
                print(f"❌ Twitter投稿失敗: {e}")
        else:
            print("❌ 投稿冷却／生成失敗")
        max_attempts -= 1
