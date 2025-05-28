import os
import time
import tweepy
from post_generator import generate_babaa_post

# 認証情報（.env または GitHub Secrets）
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Tweepy v2クライアント（App + User認証）
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

def post_to_twitter(post):
    text = f"{post['text']}\n{' '.join(post['tags'])}"
    try:
        status = api.update_status(status=text)
        print(f"✅ 投稿成功: {status.id}")
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
                print(f"❌ 投稿失敗: {e}")
        else:
            print("❌ 投稿冷却／生成失敗")
        max_attempts -= 1
