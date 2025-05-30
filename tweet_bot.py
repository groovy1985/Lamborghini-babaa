import os
import sys
import tweepy
from dotenv import load_dotenv
from post_generator import generate_babaa_post

# .env 読み込み（ローカル実行対応）
load_dotenv()

# Twitter API認証情報（GitHub Secrets or .env）
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

if not all([TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
    print("🛑 Twitter APIキーが未設定です。Secretsまたは.envを確認してください。")
    sys.exit(1)

# 認証
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
    except tweepy.errors.Forbidden as e:
        print("🚫 投稿拒否（403 Forbidden）")
        print(f"詳細: {e}")
    except tweepy.errors.TweepyException as e:
        print("🛑 Tweepyエラーが発生しました")
        print(f"詳細: {e}")
    except Exception as e:
        print("❗ その他のエラーが発生しました")
        print(f"詳細: {e}")

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

