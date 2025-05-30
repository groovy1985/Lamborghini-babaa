import os
import tweepy
import sys
from dotenv import load_dotenv
from post_generator import generate_babaa_post

# .env 読み込み
load_dotenv()

# Twitter API 認証情報の取得
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# 認証情報のバリデーション
if not all([TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
    print("🛑 Twitter APIキーが未設定です。環境変数（.env）を確認してください。")
    sys.exit(1)

# 認証処理
auth = tweepy.OAuth1UserHandler(
    TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_SECRET
)
api = tweepy.API(auth)

def post_to_twitter(text):
    try:
        api.update_status(status=text)
        print("🎉 ツイート完了")
    except tweepy.TweepError as e:
        print(f"🛑 ツイート失敗: {e}")

def main():
    post_data = generate_babaa_post()
    if not post_data:
        print("🚫 投稿スキップ（生成失敗または冷却）")
        return

    text = post_data["text"]
    print(f"📤 投稿内容:\n{text}")
    post_to_twitter(text)

if __name__ == "__main__":
    main()
