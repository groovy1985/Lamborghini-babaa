import os
import time
import tweepy
from post_generator import generate_babaa_post

# 認証情報（環境変数またはGitHub Secrets）
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Tweepy クライアント（OAuth1.0a）
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

def post_to_twitter(post):
    text = post['text']
    try:
        response = client.create_tweet(text=text)
        print(f"✅ 投稿成功: {response.data}")
    except Exception as e:
        print(f"❌ Twitter投稿失敗: {e}")

if __name__ == "__main__":
    count = 0
    max_posts = 5  # 一度に投稿する最大数
    max_attempts = 15  # 冷却などで失敗した場合の試行回数

    print("🔁 ババァ投稿生成中...")
    while count < max_posts and max_attempts > 0:
        post = generate_babaa_post()
        if post:
            post_to_twitter(post)
            count += 1
            time.sleep(3)  # 投稿間隔（秒）
        else:
            print("❌ 投稿冷却／生成失敗")
        max_attempts -= 1
