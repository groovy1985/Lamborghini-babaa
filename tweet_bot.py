import os
import sys
from datetime import datetime
import tweepy
from dotenv import load_dotenv

# === 自作モジュール読み込み ===
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from post_generator import generate_babaa_post
from shared_core.file_writer import save_raw_post

# === 環境変数の読み込み ===
load_dotenv()

def get_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"❌ 環境変数 {name} が設定されていません")
    return value

# === 投稿生成 ===
try:
    post = generate_babaa_post()
except Exception as e:
    print(f"❌ ポスト生成エラー: {e}")
    exit(1)

# === 投稿処理 ===
if post and post.get("text", "").strip():
    try:
        text = post["text"].strip()
        print(f"🕊️ 投稿中:\n{text}\n")

        client = tweepy.Client(
            consumer_key=get_env("TWITTER_API_KEY"),
            consumer_secret=get_env("TWITTER_API_SECRET"),
            access_token=get_env("TWITTER_ACCESS_TOKEN"),
            access_token_secret=get_env("TWITTER_ACCESS_SECRET"),
            bearer_token=get_env("TWITTER_BEARER_TOKEN")
        )

        response = client.create_tweet(text=text)
        tweet_url = f"https://twitter.com/user/status/{response.data['id']}"
        print(f"✅ 投稿完了: {tweet_url}")

        # === 構文寺に死体を保存 ===
        save_raw_post("baba", text)

    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
else:
    print("🚫 投稿テキストが無効です。生成に失敗した可能性あり")
