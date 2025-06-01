import os
import tweepy
from dotenv import load_dotenv
from post_generator import generate_babaa_post

# 環境変数の読み込み
load_dotenv()

# OAuth1.0a認証
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_SECRET")
)
api = tweepy.API(auth)

# 投稿生成と送信
post = generate_babaa_post()

if post and post["text"]:
    try:
        api.update_status(status=post["text"])
        print(f"🕊️ 投稿成功: {post['text']}")
    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
else:
    print("🚫 投稿生成なし：スキップ")
