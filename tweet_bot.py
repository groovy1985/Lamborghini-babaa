# tweet_bot.py

import os
import time
import tweepy
from post_generator import generate_babaa_post

# 環境変数からAPIキー取得（GitHub Secretsに設定）
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

def create_client():
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY, TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    )
    return tweepy.API(auth)

def post_to_twitter(post):
    text = f"{post['text']}\n{' '.join(post['tags'])}"
    client = create_client()
    client.update_status(status=text)
    print("✅ 投稿成功")

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
            time.sleep(3)  # スパム回避のための間隔
        else:
            print("❌ 投稿冷却／生成失敗")
        max_attempts -= 1
