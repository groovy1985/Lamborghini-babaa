import os
import sys
import json
import tweepy
from dotenv import load_dotenv
from post_generator import generate_babaa_post

load_dotenv()

# 環境変数の取得（Secrets または .env）
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# 認証情報のチェック
if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, BEARER_TOKEN]):
    print("🛑 Twitter APIキーが未設定です。Secretsまたは.envを確認してください。")
    sys.exit(1)

def save_post(text, file_path="used_posts.json"):
    try:
        used = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                used = json.load(f)
        used.append(text.strip())
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(used, f, ensure_ascii=False, indent=2)
        print("✅ 投稿内容を保存しました。")
    except Exception as e:
        print(f"⚠️ 投稿ログ保存エラー: {e}")

def post_to_twitter(text):
    try:
        print(f"🕊️ 投稿内容: {text}")
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET
        )
        response = client.create_tweet(text=text)
        print(f"✅ 投稿完了: https://twitter.com/user/status/{response.data['id']}")
        return True
    except Exception as e:
        print(f"⚠️ 投稿失敗: {e}")
        return Fal
