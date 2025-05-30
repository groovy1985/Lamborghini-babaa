import os
import tweepy
from post_generator import generate_babaa_post

# Twitter API 認証情報（環境変数から取得）
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Twitter API 認証処理
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
